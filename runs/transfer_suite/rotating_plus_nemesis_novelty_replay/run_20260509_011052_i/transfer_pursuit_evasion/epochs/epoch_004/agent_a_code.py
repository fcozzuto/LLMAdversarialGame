def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((o[0], o[1]) for o in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    xdiff = ox - sx
    ydiff = oy - sy
    prefer_x = abs(xdiff) >= abs(ydiff)

    best_move = [0, 0]
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        cap = 1 if (nx == ox and ny == oy) else 0
        man = abs(nx - ox) + abs(ny - oy)

        # Tie-break: prefer aligning along the dominant axis toward the opponent.
        nx_dir = 0 if nx == ox else (1 if nx > ox else -1)
        ny_dir = 0 if ny == oy else (1 if ny > oy else -1)
        axis_match = (nx_dir != 0 and (nx_dir == (1 if xdiff > 0 else -1))) if prefer_x else (ny_dir != 0 and (ny_dir == (1 if ydiff > 0 else -1)))
        axis_term = 0 if axis_match else 1

        # Secondary deterministic tie-break to avoid oscillations: deterministic order by (dx,dy) after metrics.
        key = (-cap, man, axis_term, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]