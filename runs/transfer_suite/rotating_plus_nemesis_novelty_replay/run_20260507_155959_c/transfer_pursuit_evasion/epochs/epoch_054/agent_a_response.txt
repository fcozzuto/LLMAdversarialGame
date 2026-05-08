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

    self_role = observation.get("self_role", "") or ""
    is_pursuer = ("purs" in self_role.lower()) or ("chaser" in self_role.lower()) or (self_role.lower() == "pursuer")

    # Candidate moves: include stay for robustness
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_move = (0, 0)
    best_val = None

    # Deterministic tie-breaking: iterate moves in fixed order
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        d_op = abs(nx - ox) + abs(ny - oy)
        # Center bias for pursuer (keeps mobility); for evader (avoid getting cornered by staying central)
        d_center = abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)
        # Corner distance (evader likes distance from pursuer by steering to far corners)
        d_corner = max(abs(nx - 0) + abs(ny - 0),
                       abs(nx - (w - 1)) + abs(ny - 0),
                       abs(nx - 0) + abs(ny - (h - 1)),
                       abs(nx - (w - 1)) + abs(ny - (h - 1)))

        # Optional "survival" proxy: avoid being adjacent to opponent when evading
        adj = (abs(nx - ox) <= 1 and abs(ny - oy) <= 1)

        if is_pursuer:
            # Pursuer: strictly reduce opponent distance; prefer central, avoid adjacency pitfalls
            val = (d_op, d_center, 0 if adj else 1)
        else:
            # Evader: maximize opponent distance; prefer moving toward corners and away from adjacency
            val = (-d_op, d_center, 0 if not adj else 1, -d_corner)

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]