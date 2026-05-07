def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = int(observation.get("self_position", [0, 0])[0]), int(observation.get("self_position", [0, 0])[1])
    ox, oy = int(observation.get("opponent_position", [w - 1, h - 1])[0]), int(observation.get("opponent_position", [w - 1, h - 1])[1])

    obstacles = observation.get("obstacles", []) or []
    obs_set = set()
    for x, y in obstacles:
        x, y = int(x), int(y)
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    resources = observation.get("resources", []) or []
    if resources:
        my_best = None
        for x, y in resources:
            x, y = int(x), int(y)
            if not (0 <= x < w and 0 <= y < h) or (x, y) in obs_set:
                continue
            md = max(abs(x - sx), abs(y - sy))
            od = max(abs(x - ox), abs(y - oy))
            margin = od - md  # positive means I can reach sooner
            # Prefer positive margin; then smaller my distance; then larger margin; then lexicographic coord
            cand = (0 if margin > 0 else 1, -margin, md, x, y)
            if my_best is None or cand < my_best[0]:
                my_best = (cand, (x, y))
        if my_best is not None:
            tx, ty = my_best[1]
            best_move = None
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = sx + dx, sy + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                        nd = max(abs(tx - nx), abs(ty - ny))
                        # Secondary term discourages steps that reduce my advantage
                        my_next = max(abs(tx - nx), abs(ty - ny))
                        opp_next = max(abs(tx - ox), abs(ty - oy))
                        score = (nd, max(0, opp_next - my_next), abs(tx - nx) + abs(ty - ny), dx, dy)
                        if best_move is None or score < best_move[0]:
                            best_move = (score, dx, dy)
            if best_move is not None:
                return [int(best_move[1]), int(best_move[2])]

    # Fallback: move toward center while avoiding obstacles
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best_move = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                d = max(abs(cx - nx), abs(cy - ny))
                score = (d, abs(dx) + abs(dy), dx, dy)
                if best_move is None or score < best_move[0]:
                    best_move = (score, dx, dy)
    if best_move is not None:
        return [int(best_move[1]), int(best_move[2])]
    return [0, 0]