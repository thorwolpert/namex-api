create table nro_names_sync_job_status(
    status_cd varchar(10) PRIMARY KEY,
    status_desc varchar(1000)
    );

create sequence nro_job_seq;

create table nro_names_sync_job(
    id integer PRIMARY KEY DEFAULT nextval('nro_job_seq'),
    status_cd varchar(10),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (status_cd) REFERENCES nro_names_sync_job_status (status_cd)
    );

create sequence nro_job_det_seq;

create table nro_names_sync_job_detail(
    id integer PRIMARY KEY DEFAULT nextval('nro_job_det_seq'),
    job_id integer,
    nr_num varchar(10),
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (job_id) REFERENCES nro_names_sync_job (id)
    );



insert into nro_names_sync_job_status(status_cd, status_desc)
values ('success', 'job succeeded');

insert into nro_names_sync_job_status(status_cd, status_desc)
values ('fail', 'job failed');

insert into nro_names_sync_job_status(status_cd, status_desc)
values ('running', 'job running');
