{
  "link_always": false, 
  "external": false, 
  "exclude_from_build": false, 
  "enable_system_call": false
}
!__DECLARATION__!
//This adds a value data to the buffer
// |**Version**|**Author**| **Date** |**Changes** 
// | 1         | NSN      | 22-06-20 | Creation
METHOD writeBool
VAR_INPUT
	value			:BOOL;				//Address of string for the filler text
END_VAR
!__IMPLEMENTATION__!
writer.writeBool(value:=value);
logChange(valPoint:=ADR(value),valType:=ESysType.tBool);