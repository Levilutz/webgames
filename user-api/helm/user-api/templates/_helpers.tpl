{{- define "user-api.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "user-api.fullname" -}}
{{- if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "user-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "user-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "user-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{- define "user-api.labels" -}}
helm.sh/chart: {{ include "user-api.chart" . }}
{{ include "user-api.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "user-api.servicePath" -}}
{{- printf "%s.%s.svc.cluster.local" (include "user-api.fullname" .) .Release.Namespace }}
{{- end }}

{{- define "user-api.dbConnectionString" -}}
{{- printf "postgresql://%s:%s@%s:5432/%s" .Values.global.postgresAdminUser .Values.global.postgresAdminPassword (include "user-api.servicePath" .) .Values.global.postgresDbName }}
{{- end }}
