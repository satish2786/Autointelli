
insert into tbl_tab(tab_name, active_yn) values('Approval_QA', 'Y');
insert into tbl_tab(tab_name, active_yn) values('Event Management_SOP', 'Y');
insert into tbl_tab(tab_name, active_yn) values('Event Management_Filters', 'Y');
insert into tbl_tab(tab_name, active_yn) values('Analytics_Exec_Summary', 'Y');
insert into tbl_tab(tab_name, active_yn) values('Analytics_Events_Analytics', 'Y');
insert into tbl_tab(tab_name, active_yn) values('Analytics_Service_Visual', 'Y');
insert into tbl_tab(tab_name, active_yn) values('Analytics_Auto_Classification', 'Y');

drop table event_data cascade;
drop table alert_data cascade;

create table event_data(
    pk_event_id bigserial primary key,
    ci_name varchar(300),
    component varchar(300),
    description varchar(2000),
    notes varchar(2000),
    severity varchar(20),
    event_created_time numeric(20,5),
    source varchar(20),
    customer_id varchar(200),
    priority varchar(10),
    value varchar(200),
    cmdline varchar(300),
    msg_updated_time varchar(100),
    fk_status_id int);
alter table event_data add constraint "event_data_fk_status_id_fkey" FOREIGN KEY (fk_status_id) REFERENCES ea_status(pk_ea_status_id);

create table alert_data(
    pk_alert_id bigserial primary key,
    ci_name varchar(300),
    component varchar(300),
    description varchar(2000),
    notes varchar(2000),
    severity varchar(20),
    event_created_time numeric(20,5),
    source varchar(20),
    customer_id varchar(200),
    priority varchar(10),
    value varchar(200),
    cmdline varchar(300),
    msg_updated_time varchar(100),
    fk_status_id int,
    fk_sop_id int);
alter table alert_data add constraint "alert_data_fk_status_id_fkey" FOREIGN KEY (fk_status_id) REFERENCES ea_status(pk_ea_status_id);


create table filters(
	pk_filter_id bigserial primary key,
	overall varchar(5),
	machine_cond varchar(20),
	machine_value varchar(100),
	application_cond varchar(20),
	application_value varchar(100),
	description_cond varchar(20),
	description_value varchar(150),
	extra_description_cond varchar(20),
	extra_description_value varchar(1000),
	value_cond varchar(20),
	value_value decimal(10,2),
	cmdline_cond varchar(20),
	cmdline_value varchar(100),
	total_event_filtered int,
	active_yn character(1));

create table sop(
	pk_sop_id bigserial primary key,
	sop_name varchar(200),
	alert_info json,
	filters json,
	sop_flow json,
	status varchar(10),
	bot_id int,
	created_by int,
	create_on timestamp,
	modified_by int,
	modified_on timestamp,
	active_yn character(1),
	applied json,
	pe_id int);

create table policyengine(
	pk_pk_id bigserial primary key,
	overall varchar(5),
	machine_cond varchar(20),
	machine_value varchar(100),
	application_cond varchar(20),
	application_value varchar(100),
	description_cond varchar(20),
	description_value varchar(150),
	extra_description_cond varchar(20),
	extra_description_value varchar(1000),
	value_cond varchar(20),
	value_value decimal(10,2),
	cmdline_cond varchar(20),
	cmdline_value varchar(100),
	applied_to_alert_total int,
	day_time_cond varchar(20),
	day_time_value varchar(100),
	sample_payload json,
	vars_payload json,
	active_yn character(1));

alter table policyengine add column batch_flag character(1);
alter table policyengine add column batch_payload json;

create table filtered_records_24(
		pk_tf_id bigserial primary key,
		fk_filter_id int,
		payload json,
		created_on timestamp);

create table filters_retention(
    pk_fret_id bigserial primary key,
    nofdays int,
    created_date timestamp,
    created_by varchar(100),
    active_yn character(1)
);
insert into filters_retention(nofdays, created_date, created_by, active_yn) values(60, now(), 'admin', 'Y');

create table is_discovery_on(is_on character(1));
insert into is_discovery_on values('N');

alter table ai_machine add column console_port int;
alter table ai_machine add column backend_port int;

alter table ai_device_credentials add column enable_yn character(1);
alter table ai_device_credentials add column enable_password varchar(200);
alter table ai_device_credentials add column version character(2);
alter table ai_device_credentials add column community_string varchar(200);
alter table ai_device_credentials add column key varchar(5000);
alter table ai_device_credentials add column passphrase varchar(200);

create table audit_videos(
	pk_audit_video_id bigserial primary key,
	alert_id varchar(20),
	ip_address varchar(30),
	user_id varchar(100),
	video_name varchar(30),
	start_datetime timestamp,
	end_datetime timestamp,
	created_by varchar(20),
	created_on timestamp,
	key varchar(128),
	key_isactive character(1));

create table batches_policyengine(
    pk_batch_id bigserial primary key,
    alert_id int,
    pe_id int,
    batch_payload json,
    sp_flow json
);

--marketplace
create table marketplace(
	pk_mp_id bigserial primary key,
	vendor varchar(100),
	machine_id int,
	payload_stdout json,
	payload_retcode character(1),
	payload_stderr varchar(300),
	active_yn character(1));

create table vmware_result(
	pk_r_id bigserial primary key,
	input_payload json,
	rawout json,
	retcode varchar(10),
	stdout json,
	stderr json,
	created_date timestamp,
	created_by varchar
);



