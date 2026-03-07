import pandas as pd
import sys

replacements = {
    "simple-examples_abs": "SimpleMethods_abs",
    "simple-examples_getMin": "SimpleMethods_getMin",
    "simple-examples_addElementToSet": "SimpleMethods_addElementToSet",
    "simple-examples_incrementNumberAtIndex": "SimpleMethods_incrementAt",
    "ArithmeticUtilsNew_subAndCheck": "ArithmeticUtils_subAndCheck",
    "polyupdate_a1": "Polyupdate_a1",
    "polyupdate_sm": "Polyupdate_sm",
    "structure_foo": "Structure_foo",
    "structure_setX": "Structure_setX",
    "listcomp02_insert_r": "ListComp02_insert_r",
    "listcomp02_insert_s": "ListComp02_insert_s",
    "map_count": "Map_count",
    "map_extend": "Map_extend",
    "map_remove": "Map_remove",
    "maxbag_add": "MaxBag_add",
    "maxbag_remove": "MaxBag_remove",
    "maxbag_getMax": "MaxBag_getMax",
    "ringbuffer_count": "RingBuffer_count",
    "ringbuffer_extend": "RingBuffer_extend",
    "ringbuffer_remove": "RingBuffer_remove",
    "ringbuffer_item": "RingBuffer_item",
    "ringbuffer_wipeOut": "RingBuffer_wipeOut",
    "doublylinkedlistnode_insertRight": "DLLN_insertRight",
    "doublylinkedlistnode_remove": "DLLN_remove",
}

# Order by class that should be respected
order = [
    "SimpleMethods",
    "StackAr",
    "QueueAr",
    "ArithmeticUtils",
    "FastMath",
    "MathUtils",
    "BooleanUtils",
    "IntMath",
    "Angle",
    "MathUtil",
    "Envelope",
    "Composite",
    "DLLN",
    "Map",
    "RingBuffer",
    "Polyupdate",
    "Structure",
    "ListComp02",
    "MaxBag"
]

def compute_avg_metrics(csv_file1, csv_file2):
    """Compute average precision and recall from two CSV files."""
    try:
        # Read both CSV files
        df1 = pd.read_csv(csv_file1)
        df2 = pd.read_csv(csv_file2)

        # Check if required columns exist
        required_cols = ['precision', 'recall']
        for col in required_cols:
            if col not in df1.columns:
                print(f"Error: Column '{col}' not found in {csv_file1}")
                sys.exit(1)
            if col not in df2.columns:
                print(f"Error: Column '{col}' not found in {csv_file2}")
                sys.exit(1)

        # Do replacements to match names in both dfs
        for old_name, new_name in replacements.items():
            df1['subject'] = df1['subject'].replace(old_name, new_name)
            df2['subject'] = df2['subject'].replace(old_name, new_name)

        # Display results
        print("\n" + "=" * 50)
        print("CSV ROWS")
        print("=" * 50)
        # for each subject present in both files, display columns subject,method,precision_one,precision_two,recall_one,recall_two
        tool_one_name = csv_file1.split('-')[0]
        tool_two_name = csv_file2.split('-')[1]
        merged_df = pd.merge(
            df1[['subject', 'method', 'tests', 'total_gt', 'precision', 'recall', 'f1_score']],
            df2[['subject', 'method', 'tests', 'total_gt', 'precision', 'recall', 'f1_score']],
            on=['subject', 'method'],
            suffixes=(tool_one_name, tool_two_name)
        )
        print("subject,method,precision_"+tool_one_name+",precision_"+tool_two_name+",recall_"+tool_one_name+",recall_"+tool_two_name+",f1_score_"+tool_one_name+",f1_score_"+tool_two_name)

        # sort by subject
        #merged_df = merged_df.sort_values(by=['subject'])
        # sort according to the defined order
        def sort_key(subject):
            for index, class_name in enumerate(order):
                if subject.startswith(class_name):
                    return index
            return len(order)
        merged_df = merged_df.sort_values(by=['subject'], key=lambda x: x.map(sort_key))

        for _, row in merged_df.iterrows():
            print(f"{row['subject']},{row['method']},{row['precision'+tool_one_name]:.2f},{row['precision'+tool_two_name]:.2f},{row['recall'+tool_one_name]:.2f},{row['recall'+tool_two_name]:.2f},{row['f1_score'+tool_one_name]:.2f},{row['f1_score'+tool_two_name]:.2f}")

        # print rows as latex,i.e., separated by &
        print("\n" + "=" * 50)
        print("LATEX ROWS")
        for _, row in merged_df.iterrows():
            subject = row['subject'].replace('_', '\_')
            print(f"{subject} & {row['total_gt'+tool_one_name]} & {row['tests'+tool_one_name]} & {row['tests'+tool_two_name]} & {row['precision'+tool_one_name]:.2f} & {row['precision'+tool_two_name]:.2f} & {row['recall'+tool_one_name]:.2f} & {row['recall'+tool_two_name]:.2f} & {row['f1_score'+tool_one_name]} & {row['f1_score'+tool_two_name]} \\\\")
        print("\midrule")

        # print avg latex row
        avg_precision_tool_one = merged_df['precision'+tool_one_name].mean()
        avg_precision_tool_two = merged_df['precision'+tool_two_name].mean()
        avg_recall_tool_one = merged_df['recall'+tool_one_name].mean()
        avg_recall_tool_two = merged_df['recall'+tool_two_name].mean()
        avg_f1_tool_one = merged_df['f1_score'+tool_one_name].mean()
        avg_f1_tool_two = merged_df['f1_score'+tool_two_name].mean()
        avg_tests_tool_one = merged_df['tests'+tool_one_name].mean()
        avg_tests_tool_two = merged_df['tests'+tool_two_name].mean()
        print(f"AVG & & {avg_tests_tool_one:.2f} & {avg_tests_tool_two:.2f} & {avg_precision_tool_one:.2f} & {avg_precision_tool_two:.2f} & {avg_recall_tool_one:.2f} & {avg_recall_tool_two:.2f} & {avg_f1_tool_one:.2f} & {avg_f1_tool_two:.2f} \\\\")
        print("=" * 50)

        # Compute averages for each file
        avg_precision_file1 = df1['precision'].mean()
        avg_recall_file1 = df1['recall'].mean()

        avg_precision_file2 = df2['precision'].mean()
        avg_recall_file2 = df2['recall'].mean()

        total_ground_truth_predicates = merged_df['total_gt'+tool_one_name].sum()

        # count cases when precision in df1 > precision in df2
        precision_better_file1 = (merged_df['precision'+tool_one_name] > merged_df['precision'+tool_two_name]).sum()
        precision_better_percentage_file1 = (precision_better_file1 / len(merged_df)) * 100

        precision_better_file2 = (merged_df['precision'+tool_one_name] < merged_df['precision'+tool_two_name]).sum()
        precision_better_percentage_file2 = (precision_better_file2 / len(merged_df)) * 100
        average_improvement = (merged_df['precision'+tool_two_name] - merged_df['precision'+tool_one_name]).mean()
        greatest_precision_increase = (merged_df['precision'+tool_two_name] - merged_df['precision'+tool_one_name]).max()

        # Display results
        print("\n" + "=" * 50)
        print("OVERALL RESULTS")
        print("=" * 50)
        print(f"Total subjects: {len(merged_df)}")
        print(f"Total Ground Truth Predicates: {total_ground_truth_predicates}")
        print(f"\nFile 1: {csv_file1}")
        print(f"  Entries: {len(df1)}")
        print(f"  Avg Precision: {avg_precision_file1:.2f}")
        print(f"  Avg Recall: {avg_recall_file1:.2f}")
        print()
        print(f"  Precision better in {tool_one_name}: {precision_better_file1} cases - {precision_better_percentage_file1:.2f}%")

        print(f"\nFile 2: {csv_file2}")
        print(f"  Entries: {len(df2)}")
        print(f"  Avg Precision: {avg_precision_file2:.2f}")
        print(f"  Avg Recall: {avg_recall_file2:.2f}")
        print()
        print(f"  Precision better in {tool_two_name}: {precision_better_file2} cases - {precision_better_percentage_file2:.2f}%")
        print(f"  Average Precision Improvement from {tool_one_name} to {tool_two_name}: {average_improvement:.2f}%")
        print(f"  Greatest Precision Increase from {tool_one_name} to {tool_two_name}: {greatest_precision_increase:.2f}%")
        print("=" * 50)

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print("Usage: python compute_avg_metrics.py <csv_file1> <csv_file2>")
        sys.exit(1)

    csv_file1 = sys.argv[1]
    csv_file2 = sys.argv[2]

    compute_avg_metrics(csv_file1, csv_file2)


if __name__ == "__main__":
    main()