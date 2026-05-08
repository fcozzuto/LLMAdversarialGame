def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obs

    def cheb(x, y):
        return max(abs(x - ox), abs(y - oy))

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    role = (observation.get("self_role") or "").lower()
    pursuer = "pursuer" in role

    # Corner that tends to force/tempt zigzags
    if pursuer:
        # As pursuer, try to drive opponent toward the corner that is farthest from us.
        tx, ty = max(corners, key=lambda c: (cheb(c[0], c[1]), -(c[0] == 0 or c[0] == w - 1) - (c[1] == 0 or c[1] == h - 1)))
    else:
        # As evader, flee toward the corner farthest from opponent.
        tx, ty = max(corners, key=lambda c: max(abs(c[0] - ox), abs(c[1] - oy)))

    best_dxdy = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # Encourage monotonic progress toward the chosen corner/axis.
        prog = -max(abs(nx - tx), abs(ny - ty))
        dist = cheb(nx, ny)
        # If pursuer: minimize dist; also reduce opponent mobility by going "ahead" along corner axis.
        # If evader: maximize dist; also move along corner direction.
        if pursuer:
            axis_ahead = (1 if (nx - ox) * (tx - ox) > 0 else 0) + (1 if (ny - oy) * (ty - oy) > 0 else 0)
            key = (dist, -axis_ahead, -prog, dx, dy)
        else:
            axis_ahead = (1 if (nx - ox) * (tx - ox) > 0 else 0) + (1 if (ny - oy) * (ty - oy) > 0 else 0)
            # Prefer diagonals toward target; deterministic tie-break by move order via dx,dy.
            key = (-dist, -prog, -axis_ahead, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_dxdy = [dx, dy]
        # Immediate capture if adjacent at radius 0
        if (nx, ny) == (ox, oy) and pursuer:
            return [dx, dy]
    return best_dxdy