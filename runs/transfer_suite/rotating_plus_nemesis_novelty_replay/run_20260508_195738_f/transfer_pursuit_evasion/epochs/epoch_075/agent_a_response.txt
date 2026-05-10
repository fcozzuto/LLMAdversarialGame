def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    self_role = str(observation.get("self_role", "") or "").lower()
    opp_role = str(observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role)  # pursuer tends to chase

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    corner_boost = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    man = lambda x1, y1, x2, y2: abs(x1 - x2) + abs(y1 - y2)

    best = None
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d = man(nx, ny, ox, oy)
        # Obstacle-aware: avoid stepping next to obstacles (more important for evader).
        adj_obs = 0
        for ox2, oy2 in obstacles:
            if man(nx, ny, ox2, oy2) == 1:
                adj_obs += 1

        if self_is_pursuer:
            # Pursuer: minimize distance; also reduce "freedom" for evader by approaching corners slightly.
            corner_near = min(man(nx, ny, cx, cy) for cx, cy in corner_boost)
            score = -d * 10 - adj_obs * 2 - corner_near * 0.05
        else:
            # Evader: maximize distance; prefer corners and avoid obstacle adjacency.
            corner_far = min(man(nx, ny, cx, cy) for cx, cy in corner_boost)
            score = d * 10 - adj_obs * 4 + corner_far * 0.1

        if best is None or (score > best_score + 1e-12) or (best_score is not None and abs(score - best_score) <= 1e-12):
            if best is None:
                best, best_score = (dx, dy), score
            else:
                # Deterministic tie-break: prefer moves that change both axes, then dx, then dy, then staying last.
                def rank(m):
                    rdx, rdy = m
                    diag = 1 if (rdx != 0 and rdy != 0) else 0
                    stay = 1 if (rdx == 0 and rdy == 0) else 0
                    return (diag, -abs(rdx), -abs(rdy), -stay)
                if rank((dx, dy)) > rank(best):
                    best, best_score = (dx, dy), score

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]