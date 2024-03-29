for OUTPUT in $(ls input_module_*.py | xargs -L1 | awk -F"input_module_" '{print $2}')
do
    echo $OUTPUT
    # Now let's go to work on the single source code 
    # -------------------------------------------------------------------------------
    # Remove these:
    #   1. The old import $AOB_TA_DIR_lowercase_declare statement
    #   2. The old import input_module_$OUTPUT as input_module statement 
    #   3. The old from solnlib.packages.splunklib import modularinput as smi  statement
    #   4. The old import modinput_wrapper.base_modinput statement
    #   5. The old "Do Not Edit" lines from AOB code generation
    # -------------------------------------------------------------------------------
    new_input_source=$(echo "$new_input_source" | sed "/^import .*_declare$/d")
    new_input_source=$(echo "$new_input_source" | sed '/^import input_module_/d')
    new_input_source=$(echo "$new_input_source" | sed '/^from solnlib.packages.splunklib import modularinput as smi/d')
    new_input_source=$(echo "$new_input_source" | sed '/import modinput_wrapper.base_modinput/d')
    new_input_source=$(echo "$new_input_source" | sed '/Do not edit this file!!!/,/Add your modular input logic to file/d')

    # -------------------------------------------------------------------------------
    # change the reference for base_modinput to use the name in the imports.py 
    # -------------------------------------------------------------------------------
    new_input_source=$(echo "$new_input_source" | sed 's/(modinput_wrapper.base_modinput./(base_mi./')

    # -------------------------------------------------------------------------------
    # set single instance mode to false and remove excess code from $OUTPUT
    # -------------------------------------------------------------------------------
    # Remove the if then logic and set the variable to False and fix the indentation
    new_input_source=$(echo "$new_input_source" | sed "/^        if 'use_single_instance_mode' /,/use_single_instance = False/{/use_single_instance = False/p;d;}" | sed 's/^            use_single_instance = False/        use_single_instance = False/')
    #echo "$new_input_source"

    # -------------------------------------------------------------------------------
    # get the validate_input code generated by AOB in the input_module_XXX file and insert it here  (with indentation & removal of 'helper')
    # -------------------------------------------------------------------------------
    VALIDATION=$(sed -n '/^def validate_input(helper, definition):/,/^def /{ /^def validate_input(/p; /^def /d; p;};' input_module_$OUTPUT | sed 's/\(.*\)/    \1/' )
    #echo "$VALIDATION"

    # now we need to replace the AOB helper call with the actual validation logic from above and remove the original lines
    #######new_input_source=${new_input_source/        input_module.validate_input(self, definition)/"$VALIDATION"}     <--  REMOVED for 10x performance improvement
    new_input_source=$(echo "$new_input_source" | sed '/        input_module.validate_input(self, definition)/r'<(echo "$VALIDATION"))
    # remove the old function call & comment
    new_input_source=$(echo "$new_input_source" | sed '/    def validate_input(self, definition):/d' | sed '/    """validate the input stanza"""/d' | sed '/        input_module.validate_input(self, definition)/d' )
    #echo "$new_input_source"

    # -------------------------------------------------------------------------------
    #   get the collect_events code from the input_module_XXX file and insert it here
    # -------------------------------------------------------------------------------
    COLLECT_EVENTS=$(sed -n '/^def collect_events(helper, ew):/,/^def /{ /^def collect_events(/p; /(^def |$)/d; p;}' input_module_$OUTPUT | sed 's/\(.*\)/    \1/' | sed '1d')
    #echo COLLECT_EVENTS="$COLLECT_EVENTS" 

    # replace the original collect_events with the actual collect_events logic from the input_module_$OUTPUT file
    #######new_input_source=${new_input_source/        input_module.collect_events(self, ew)/"$COLLECT_EVENTS"}     <--  REMOVED for 10x performance improvement
    new_input_source=$(echo "$new_input_source" | sed '/        input_module.collect_events(self, ew)/r'<(echo "$COLLECT_EVENTS"))
    # remove the old function call & comment
    new_input_source=$(echo "$new_input_source" | sed '/^    def collect_events(self, ew):/d' | sed '/^        """write out the events"""/d' | sed '/        input_module.collect_events(self, ew)/d' )
    #echo "$new_input_source"


    # set the ta_config filename
    new_input_source=${new_input_source//CONF_NAME/CONF_NAME = \""$AOB_TA_DIR_lowercase"\"}

    # Overwrite out the mod input source code file with this new code
    echo "$new_input_source" > $OUTPUT
    echo Done.   
done