def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    opp = set((p[0], p[1]) for p in (observation.get("opponent_territory", []) or []))
    unclaimed = set((p[0], p[1]) for p in (observation.get("unclaimed_cells", []) or []))
    selft = set((p[0], p[1]) for p in (observation.get("self_territory", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(a, b): return 0 <= a < w and 0 <= b < h
    def adj_opp(a, b):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: 
                    continue
                if (a + dx, b + dy) in opp:
                    return True
        return False
    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # Strategic shift: attack opponent frontier and counterclaim; if blocked, expand toward unclaimed.
    best = (-10**18, (0, 0))
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        enters_opp = (nx, ny) in opp
        near_opp = adj_opp(nx, ny)
        enters_un = (nx, ny) in unclaimed or (nx, ny) not in opp and (nx, ny) not in selft
        dist_to_opp = 10**6
        if opp:
            dist_to_opp = min(cheb if False else (abs(nx - px) + abs(ny - py)) for (px, py) in opp)
        # Deterministic score: prioritize flipping by stepping into opponent territory, then frontier adjacency.
        score = 0
        if enters_opp:
            score += 1000
            score += 20 - man(nx, ny, ox, oy) * 0.2
        if near_opp and not enters_opp:
            score += 160
            score += 10 - man(nx, ny, ox, oy) * 0.05
        if enters_un:
            score += 25
        # Keep some cohesion while advancing: avoid walking too far from current mass center
        if selft:
            cx = sum(px for px, _ in list(selft)[:8]) / float(min(8, len(selft)))  # bounded
            cy = sum(py for _, py in list(selft)[:8]) / float(min(8, len(selft)))
            score += -0.02 * (abs(nx - cx) + abs(ny - cy))
        # Tie-breakers: lower dx, then lower dy, then lexicographic position
        score -= 0.001 * (dist_to_opp if opp else 0)
        cand = (score, (dx, dy))
        if cand[0] > best[0] or (cand[0] == best[0] and cand[1] < best[1]):
            best = cand

    # If somehow no legal move, stay.
    dx, dy = best[1] if best[1] else (0, 0)
    return [int(dx), int(dy)]