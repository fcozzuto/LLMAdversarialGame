def choose_move(observation):
    W = observation.get("grid_width", 8)
    H = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [W - 1, H - 1])
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            obstacles.add((p[0], p[1]))
    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2 and (r[0], r[1]) not in obstacles:
            resources.append((r[0], r[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in obstacles:
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def score_for_move(dx, dy):
        nx, ny = sx + dx, sy + dy
        if resources:
            # Consider only the closest few targets for speed/determinism.
            ordered = sorted(resources, key=lambda t: (man((sx, sy), t), t[0], t[1]))
            candidates = ordered[: min(6, len(ordered))]
            best = None
            for tx, ty in candidates:
                our = man((nx, ny), (tx, ty))
                opp = man((ox, oy), (tx, ty))
                # Advantage: larger means we're closing the race.
                advantage = opp - our
                # Tie-breakers: closer first, then deterministic coordinate.
                key = (advantage, -our, - (tx + 17 * ty))
                if best is None or key > best[0]:
                    best = (key, tx, ty)
            # Small secondary preference to keep moving.
            return best[0] + (0 if (dx == 0 and dy == 0) else -1,)
        # No resources: move toward center.
        cx, cy = (W - 1) // 2, (H - 1) // 2
        d = man((nx, ny), (cx, cy))
        key = (-d, -(nx + 17 * ny), 0 if (dx == 0 and dy == 0) else -1)
        return key

    best_move = None
    best_key = None
    for dx, dy in legal:
        k = score_for_move(dx, dy)
        if best_key is None or k > best_key:
            best_key = k
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]