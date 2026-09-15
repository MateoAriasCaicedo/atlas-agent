from atlas.pipelines.pipelines import research_pipeline


def main():
    state = research_pipeline("Impact of AI on the 2026 job market.")
    print(state)


if __name__ == "__main__":
    main()
