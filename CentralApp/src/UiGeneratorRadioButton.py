'''
Created on Feb 4, 2012

@author: Ken
'''

from UiGeneratorControl import UiGenControl

class RadioButtonUiGenControl( UiGenControl ):
    attr_def = None

    def __init__(self, attr_def):
        self.attr_def = attr_def

    def gen_xml_string(self, above_name):
    
        xml_str =  "    <!-- Begin NAME field text label and radio group -->\n"
        xml_str += "    <TextView\n"
        xml_str += "        android:id=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_width=\"120dp\"\n"
        xml_str += "        android:layout_height=\"40dp\"\n"
        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:gravity=\"center_vertical|right\"\n"
        xml_str += "        android:text=\"NAME:\" />\n"
        xml_str += "\n"
        xml_str += "    <RadioGroup\n"
        xml_str += "        android:id=\"@+id/NAMERadioGroup\"\n"
        xml_str += "        android:layout_width=\"600dp\"\n"
        xml_str += "        android:layout_height=\"40dp\"\n"
        xml_str += "        android:layout_below=\"@+id/ABOVELabel\"\n"
        xml_str += "        android:layout_toRightOf=\"@+id/NAMELabel\"\n"
        xml_str += "        android:layout_alignTop=\"@+id/NAMELabel\"\n"
        xml_str += "        android:orientation=\"horizontal\" >\n"
        xml_str += "\n"
    
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        for token in tokens:        
            xml_str += "        <RadioButton\n"
            xml_str += "            android:id=\"@+id/NAMEBUTTONRadioButton\"\n"
            xml_str += "            android:layout_width=\"wrap_content\"\n"
            xml_str += "            android:layout_height=\"wrap_content\"\n"
            xml_str += "            android:text=\"BUTTON\" />\n"
            xml_str += "\n"
            name, token_val = token.split('=')
            xml_str = xml_str.replace('BUTTON',name) 
    
        if self.attr_def['Options'] == 'Clear':
            xml_str += "        <RadioButton\n"
            xml_str += "            android:id=\"@+id/NAMEClearRadioButton\"\n"
            xml_str += "            android:layout_width=\"wrap_content\"\n"
            xml_str += "            android:layout_height=\"wrap_content\"\n"
            xml_str += "            android:text=\"Clear\" />\n"
            xml_str += "\n"

        xml_str += "    </RadioGroup>\n"
        xml_str += "    <!-- End NAME field text label and radio group -->\n\n"
        return xml_str

    def gen_java_declarations_string(self):
        java_str  = "    private RadioGroup NAMERadioGroup;\n"
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        for token in tokens:        
            java_str += "    private RadioButton NAMEBUTTONRadioButton;\n"
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name) 
    
        if self.attr_def['Options'] == 'Clear':
            java_str += "    private RadioButton NAMEClearRadioButton;\n"
        return java_str

    def gen_java_init_string(self):
        java_str  = "        NAMERadioGroup = (RadioGroup) findViewById(R.id.NAMERadioGroup);\n"
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        for token in tokens:        
            java_str += "        NAMEBUTTONRadioButton = (RadioButton) findViewById(R.id.NAMEBUTTONRadioButton);\n"
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name)
    
        if self.attr_def['Options'] == 'Clear':
            java_str += "        NAMEClearRadioButton = (RadioButton) findViewById(R.id.NAMEClearRadioButton);\n"
        return java_str

    def gen_java_button_handler(self):
        java_str = ''
        if (self.attr_def['Options'] == 'Clear'):      
            java_str += '        NAMERadioGroup.setOnCheckedChangeListener(new RadioGroup.OnCheckedChangeListener() {\n\n'
            java_str += '            @Override\n'
            java_str += '            public void onCheckedChanged(RadioGroup group, int checkedId) {\n'
            java_str += "                unsavedChanges = true;\n"
            java_str += '                if ( checkedId == R.id.NAMEClearRadioButton ) {\n'
            java_str += '                    group.clearCheck();\n'
            java_str += '                }\n'
            java_str += '            }\n'
            java_str += '        });\n'
        return java_str

    def gen_java_discard_handler(self):
        java_str = "        NAMERadioGroup.clearCheck();\n"
        return java_str

    def gen_java_save_handler(self):
        java_str = "\n        String NAMESelection = \"NAME:\";\n"
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        first = True
        for token in tokens:
            if (first == True):
                first = False
                java_str += "        if (NAMEBUTTONRadioButton.isChecked())\n"
                java_str += "            buffer.append(NAMESelection + NAMEBUTTONRadioButton.getText().toString() + eol);\n"
            else:
                java_str += "        else if (NAMEBUTTONRadioButton.isChecked())\n"
                java_str += "            buffer.append(NAMESelection + NAMEBUTTONRadioButton.getText().toString() + eol);\n"
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name)
        return java_str
    
    def gen_java_reload_handler(self):
        java_str = "                } else if ( token.equalsIgnoreCase(\"NAME\")) {\n"
        java_str += "                    String valueStr = tokenizer.nextToken();\n"
        map_values = self.attr_def['Map_Values']
        tokens = map_values.split(':')
        first = True
        for token in tokens:
            if (first == True):
                first = False
                java_str += "                    if ( valueStr.equalsIgnoreCase(\"BUTTON\") )\n"
                java_str += "                        NAMERadioGroup.check(R.id.NAMEBUTTONRadioButton);\n"
            else:
                java_str += "                    else if ( valueStr.equalsIgnoreCase(\"BUTTON\") )\n"
                java_str += "                        NAMERadioGroup.check(R.id.NAMEBUTTONRadioButton);\n"
            name, token_val = token.split('=')
            java_str = java_str.replace('BUTTON',name) 
        return java_str

