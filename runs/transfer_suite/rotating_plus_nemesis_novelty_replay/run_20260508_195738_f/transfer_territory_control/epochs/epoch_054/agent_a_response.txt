def choose_move(observation):
    x, y = observation.get("self_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    opp_list = list(opp)
    opp_samples = opp_list[:20] if len(opp_list) > 20 else opp_list
    self_list = list(selft)[:40]
    un_list = list(unclaimed)[:40]

    def min_manh_to_set(nx, ny, s_list):
        if not s_list:
            return 10**9
        md = 10**9
        for px, py in s_list:
            d = abs(px - nx) + abs(py - ny)
            if d < md:
                md = d
        return md

    def frontier_bonus(nx, ny):
        if (nx, ny) in selft:
            return 0.5
        # Encourage stepping adjacent to our territory (fights edge sniping by staying cohesive)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                ax, ay = nx + dx, ny + dy
                if (ax, ay) in selft:
                    return 1.2
        return 0.0

    best_score = -10**18
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        score = 0.0
        if (nx, ny) in opp:
            score += 7.5  # flipping opponent territory
        elif (nx, ny) in unclaimed:
            score += 4.0
        elif (nx, ny) in selft:
            score += 1.0

        d_opp = min_manh_to_set(nx, ny, opp_samples)
        if opp_samples:
            score += -0.35 * d_opp

        if un_list:
            d_un = min_manh_to_set(nx, ny, un_list)
            score += -0.12 * d_un

        score += frontier_bonus(nx, ny)

        # Small bias: prefer not changing both coordinates unless it also moves closer to targets
        if dx != 0 and dy != 0:
            score -= 0.1

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]