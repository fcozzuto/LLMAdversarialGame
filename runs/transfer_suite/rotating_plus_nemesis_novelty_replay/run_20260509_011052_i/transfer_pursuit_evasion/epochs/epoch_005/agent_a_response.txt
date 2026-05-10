def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((o[0], o[1]) for o in observation.get("obstacles", []))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def step_toward(a, b):
        return 0 if a == b else (1 if b > a else -1)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    role = observation.get("self_role", "pursuer")
    is_evader = role.lower() == "evader"
    # Deterministic tie-break order
    dirs = sorted(dirs, key=lambda d: (d[0], d[1]))

    best = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue

        cap = 1 if (nx == ox and ny == oy and observation.get("capture_radius", 0) == 0) else 0
        cheb = max(abs(nx - ox), abs(ny - oy))
        man = abs(nx - ox) + abs(ny - oy)

        # Obstacle / boundary avoidance: penalize staying still behind "wall"
        blocked = 0
        for tx in (-1, 0, 1):
            for ty in (-1, 0, 1):
                if tx == 0 and ty == 0:
                    continue
                ax, ay = nx + tx, ny + ty
                if not (0 <= ax < w and 0 <= ay < h) or (ax, ay) in obstacles:
                    blocked += 1

        if is_evader:
            # Flee: maximize distance; also prefer reducing path-blocking.
            # If corners are safe, move toward the farthest corner.
            corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
            far_corner = max(corners, key=lambda c: max(abs(c[0] - nx), abs(c[1] - ny)))
            corner_dir = (step_toward(nx, far_corner[0]), step_toward(ny, far_corner[1]))
            corner_align = 0 if (corner_dir[0] == dx and corner_dir[1] == dy) else 1
            key = (0 - cap, -cheb, -man, blocked, corner_align, dx, dy)
        else:
            # Chase: minimize distance; capture dominates; prefer moves that keep options open.
            # Add a slight nudge toward direct direction to prevent oscillation.
            direct_dx = step_toward(sx, ox)
            direct_dy = step_toward(sy, oy)
            direct_align = 0 if (dx == direct_dx and dy == direct_dy) else 1
            key = (-cap, cheb, man, blocked, direct_align, dx, dy)

        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return best_move