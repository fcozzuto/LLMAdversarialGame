def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    self_role = observation.get("self_role", "pursuer") or "pursuer"
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p is not None and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) if abs(dx) > abs(dy) else abs(dy)

    def corners():
        cs = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        cs2 = [c for c in cs if c not in obstacles]
        return cs2 if cs2 else cs

    prev_d = cheb((x, y), (ox, oy))
    my_corners = corners()

    # Farthest-corner target for evasion; nearest-corner target for pursuit (role-based usage below).
    def corner_score(c):
        return cheb(c, (ox, oy))

    far_corner = max(my_corners, key=corner_score)
    near_corner = min(my_corners, key=corner_score)

    target = far_corner if "evader" in self_role else near_corner

    best_move = [0, 0]
    best_val = None

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            continue
        nd = cheb((nx, ny), (ox, oy))
        step_towards = abs(nx - target[0]) + abs(ny - target[1])
        prev_towards = abs(x - target[0]) + abs(y - target[1])

        # Prefer movement along the chosen target direction; keep tie-breaking deterministic.
        # Also add obstacle proximity penalty by checking adjacent cells.
        adj_block = 0
        for ax, ay in [(nx - 1, ny), (nx + 1, ny), (nx, ny - 1), (nx, ny + 1)]:
            if (ax, ay) in obstacles:
                adj_block += 1

        if "evader" in self_role:
            # Maximize distance and drift toward far corner (unless already there).
            val = (nd * 100.0) + ((nd - prev_d) * 30.0) + ((prev_towards - step_towards) * 2.0) - (adj_block * 5.0)
        else:
            # Pursuer: minimize distance; if not improving, still move to reduce Manhattan to the evader's corner target.
            val = (-nd * 100.0) + ((prev_d - nd) * 30.0) + ((prev_towards - step_towards) * -2.0) - (adj_block * 5.0)

        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move