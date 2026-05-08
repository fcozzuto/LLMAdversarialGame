def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    role = (observation.get("self_role", "") or "").lower()
    is_pursuer = ("purs" in role) or ("chaser" in role) or ("chase" in role) or ("pursuer" in role)

    # For pursuer, try a mild "intercept" by targeting a point mirrored beyond the opponent from our side.
    tx = ox if not is_pursuer else max(0, min(w - 1, 2 * ox - sx))
    ty = oy if not is_pursuer else max(0, min(h - 1, 2 * oy - sy))

    best_move = (0, 0)
    best_val = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d_opp = abs(nx - ox) + abs(ny - oy)
        d_tar = abs(nx - tx) + abs(ny - ty)
        # pursuer: minimize distance to opponent (and to intercept); evader: maximize.
        val = (d_opp * 10 + d_tar) if is_pursuer else -(d_opp * 10 + d_tar)

        # Deterministic tie-break: prefer larger x-progress toward desired direction, then y, then non-stay.
        desired_dx = 0
        desired_dy = 0
        if is_pursuer:
            desired_dx = 1 if ox > nx else (-1 if ox < nx else 0)
            desired_dy = 1 if oy > ny else (-1 if oy < ny else 0)
        else:
            desired_dx = -1 if ox > nx else (1 if ox < nx else 0)
            desired_dy = -1 if oy > ny else (1 if oy < ny else 0)

        tb = (0 if (dx, dy) != (0, 0) else -1,
              1 if dx == desired_dx else 0,
              1 if dy == desired_dy else 0,
              -abs(dx) - abs(dy))

        if best_val is None:
            best_val = val
            best_move = (dx, dy)
            best_tb = tb
        else:
            if val > best_val if not is_pursuer else val < best_val:
                best_val = val
                best_move = (dx, dy)
                best_tb = tb
            elif val == best_val:
                if tb > best_tb:
                    best_move = (dx, dy)
                    best_tb = tb

    return [int(best_move[0]), int(best_move[1])]