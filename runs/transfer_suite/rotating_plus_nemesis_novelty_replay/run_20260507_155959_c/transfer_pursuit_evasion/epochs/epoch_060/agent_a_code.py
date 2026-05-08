def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((int(x), int(y)))
        except Exception:
            pass

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]
    role = (observation.get("self_role", "") or "").lower()
    is_evader = ("evad" in role) or ("runner" in role)

    def score(nx, ny):
        # obstacle-aware greedy: prefer moving that changes shortest-step alignment
        d = abs(nx - ox) + abs(ny - oy)
        if is_evader:
            base = 1000 - d  # larger d is better -> smaller base
            # also avoid moves that immediately let pursuer "approach" next
            step_moves = [(-1, -1), (0, -1), (1, -1),
                          (-1, 0), (0, 0), (1, 0),
                          (-1, 1), (0, 1), (1, 1)]
            min_after = 10**9
            for adx, ady in step_moves:
                ax, ay = ox + adx, oy + ady
                if not valid(ax, ay):
                    continue
                min_after = min(min_after, abs(ax - nx) + abs(ay - ny))
            # if opponent can reduce quickly, penalize
            return base + 5 * min_after
        else:
            # pursuer: minimize distance; discourage getting cornered near edges behind obstacles
            base = d
            # penalize being adjacent to obstacles in many directions (can cause boundary hits)
            neigh = 0
            for adx, ady in moves:
                ax, ay = nx + adx, ny + ady
                if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                    neigh += 1
            # prefer center a bit
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            center = abs(nx - cx) + abs(ny - cy)
            return base + 0.3 * neigh + 0.05 * center

    best_move = [0, 0]
    best_val = None
    # deterministic tie-break: fixed iteration order; no random
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        v = score(nx, ny)
        if best_val is None or v < best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move