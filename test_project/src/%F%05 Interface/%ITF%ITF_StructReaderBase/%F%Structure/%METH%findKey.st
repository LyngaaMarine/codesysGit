{
  "link_always": false, 
  "external": false, 
  "exclude_from_build": false, 
  "enable_system_call": false
}
!__DECLARATION__!
//This method finds a key by name in the selected structure
METHOD findKey : EStructType
VAR_INPUT
	name			:POINTER TO EASCII;		//Address of the name to find, only input string address or zero terminated byte array
END_VAR

!__IMPLEMENTATION__!
