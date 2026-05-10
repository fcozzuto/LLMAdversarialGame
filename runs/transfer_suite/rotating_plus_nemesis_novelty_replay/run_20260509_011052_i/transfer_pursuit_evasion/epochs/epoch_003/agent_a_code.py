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

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        cap = 1 if (nx == ox and ny == oy) else 0
        man = abs(nx - ox) + abs(ny - oy)

        # Axis-aligned tie-break helps against zigzag evasions.
        nx_dir = 0 if nx == ox else (1 if nx > ox else -1)
        ny_dir = 0 if ny == oy else (1 if ny > oy else -1)
        axis_term = (0 if (prefer_x and nx_dir == (1 if xdiff > 0 else (-1 if xdiff < 0 else 0))) else 1) if prefer_x else \
                    (0 if (not prefer_x and ny_dir == (1 if ydiff > 0 else (-1 if ydiff < 0 else 0))) else 1)

        key = (-cap, man, axis_term, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    return best if best is not None else [0, 0]