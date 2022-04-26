{{- define "user-api.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "user-api.fullname" -}}
{{- if contains .Chart.Name .Release.Name }}
{{- .Release.Name | trunc (int (sub 63 10)) | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "user-api.fullname-postgres" -}}
{{- printf "%s-postgres" (include "user-api.fullname" .) }}
{{- end }}

{{- define "user-api.fullname-migrate" -}}
{{- printf "%s-migrate" (include "user-api.fullname" .) }}
{{- end }}

{{- define "user-api.tag-api" -}}
{{- if and (not .Values.global.tagBaseOverride) (not .Values.image.tag) (not .Values.image.tagBase) }}
{{- fail "Image for api requires at least some tag set" }}
{{- end }}
{{- if .Values.image.tag }}
{{- .Values.image.tag }}
{{- else }}
{{- printf "%s-%s" (default .Values.image.tagBase .Values.global.tagBaseOverride) .Values.image.tagContainer }}
{{- end }}
{{- end }}

{{- define "user-api.tag-migrate" -}}
{{- if and (not .Values.global.tagBaseOverride) (not .Values.migrate.image.tag) (not .Values.migrate.image.tagBase) }}
{{- fail "Image for migrate requires at least some tag set" }}
{{- end }}
{{- if .Values.migrate.image.tag }}
{{- .Values.migrate.image.tag }}
{{- else }}
{{- printf "%s-%s" (default .Values.migrate.image.tagBase .Values.global.tagBaseOverride) .Values.migrate.image.tagContainer }}
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

{{- define "user-api.db-dnsname" -}}
{{- printf "%s.%s.svc.cluster.local" (include "user-api.fullname-postgres" .) .Release.Namespace }}
{{- end }}
