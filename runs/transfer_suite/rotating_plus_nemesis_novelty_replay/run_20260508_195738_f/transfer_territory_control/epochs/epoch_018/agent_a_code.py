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

    cand = []
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        base = 0.0
        if (nx, ny) in selft:
            base += 2.0
        elif (nx, ny) in opp:
            base += 8.0  # counter-claim pressure
        elif (nx, ny) in unclaimed:
            base += 4.0
        else:
            base += 1.0  # neutral/unknown

        # Frontier incentive: move toward where it helps us touch more cells
        adj_own = 0
        adj_opp = 0
        adj_un = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx == 0 and ddy == 0:
                    continue
                ax, ay = nx + ddx, ny + ddy
                if not inb(ax, ay) or (ax, ay) in obs:
                    continue
                if (ax, ay) in selft:
                    adj_own += 1
                elif (ax, ay) in opp:
                    adj_opp += 1
                elif (ax, ay) in unclaimed:
                    adj_un += 1

        # If stepping into opponent territory, avoid being immediately surrounded
        surround_pen = 0.0
        if (nx, ny) in opp:
            surround_pen = 2.0 * max(0, adj_opp - 2) - 0.5 * adj_own

        # Distance-to-unclaimed (keep claiming forward)
        md_un = 999999
        if unclaimed:
            # sample a few deterministically to stay cheap
            samples = 0
            for cx, cy in sorted(unclaimed)[:min(12, len(unclaimed))]:
                d = abs(cx - nx) + abs(cy - ny)
                if d < md_un:
                    md_un = d
                samples += 1
        else:
            md_un = 10

        score = base + 0.7 * adj_own + 0.4 * adj_un - 0.6 * adj_opp - surround_pen - 0.05 * md_un
        # Tiebreaker: prefer moves that reduce manhattan distance to nearest opp territory cell (deterministic)
        md_opp = 999999
        if opp:
            for ox, oy in sorted(opp)[:min(10, len(opp))]:
                d = abs(ox - nx) + abs(oy - ny)
                if d < md_opp:
                    md_opp = d
        else:
            md_opp = 10
        score -= 0.02 * md_opp
        cand.append((score, dx, dy))

    if not cand:
        return [0, 0]
    cand.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [int(cand[0][1]), int(cand[0][2])]