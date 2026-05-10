def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    x, y = int(sp[0]), int(sp[1])

    self_t = observation.get("self_territory") or []
    opp_t = observation.get("opponent_territory") or []
    obs_list = observation.get("obstacles") or []
    unclaimed = observation.get("unclaimed_cells") or []

    self_set = set((int(p[0]), int(p[1])) for p in self_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    opp_set = set((int(p[0]), int(p[1])) for p in opp_t if isinstance(p, (list, tuple)) and len(p) >= 2)
    blocked = set((int(p[0]), int(p[1])) for p in obs_list if isinstance(p, (list, tuple)) and len(p) >= 2)
    targets = [(int(p[0]), int(p[1])) for p in unclaimed if isinstance(p, (list, tuple)) and len(p) >= 2]

    def dist_to_targets(px, py):
        if not targets:
            return 10**9
        best = 10**9
        for tx, ty in targets:
            d = abs(tx - px) + abs(ty - py)
            if d < best:
                best = d
        return best

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_score = -10**18
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in blocked:
            continue

        score = 0
        if (nx, ny) in self_set:
            score += 2
        if (nx, ny) in opp_set:
            score -= 3
        if (nx, ny) not in self_set and (nx, ny) not in opp_set:
            if (nx, ny) in targets:
                score += 5

        score += -0.2 * dist_to_targets(nx, ny)

        # Mild bias away from opponent-controlled area (territory_edge_claim archetype)
        if opp_set:
            mind = 10**9
            for ox, oy in (list(opp_set)[:48] if len(opp_set) > 48 else opp_set):
                d = abs(ox - nx) + abs(oy - ny)
                if d < mind:
                    mind = d
            score += 0.05 * mind

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move