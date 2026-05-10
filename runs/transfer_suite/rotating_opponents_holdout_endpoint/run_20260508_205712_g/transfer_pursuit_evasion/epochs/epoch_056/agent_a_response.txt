def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for a in observation.get("obstacles", []) or []:
        if isinstance(a, (list, tuple)) and len(a) >= 2:
            x, y = int(a[0]), int(a[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    role = (observation.get("self_role", "pursuer") or "pursuer").lower()
    pursuer = role != "evader"

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return (x, y) not in obstacles

    best = None
    best_val = None

    # Deterministic tie-break: fixed move order already.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) != (sx, sy) and not free(nx, ny):
            continue

        # Distance metric: Chebyshev (diagonal moves reduce both axes)
        dist = max(abs(nx - ox), abs(ny - oy))

        # Additional shaping to avoid oscillation and wall hugging:
        # - prefer moves that reduce Manhattan change towards a stable corner (evader) or away (pursuer)
        mx = 0
        # Corner targets for evader (alternate deterministically by turn_index)
        ti = int(observation.get("turn_index", 0) or 0)
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        corner = corners[ti % 4]
        cx, cy = corner

        # If evader: maximize distance; also prefer being closer to a chosen corner (safer pathing)
        # If pursuer: minimize distance; also prefer moving toward the opponent's line relative to corner
        if pursuer:
            val = -dist
            # Slight preference: move that also decreases distance to opponent's position along both axes
            # and doesn't step away from opponent by Manhattan.
            mcur = abs(sx - ox) + abs(sy - oy)
            mnew = abs(nx - ox) + abs(ny - oy)
            val += 0.02 * (mnew - mcur)  # prefer smaller mnew => negative delta
        else:
            val = dist
            dcorner_old = abs(sx - cx) + abs(sy - cy)
            dcorner_new = abs(nx - cx) + abs(ny - cy)
            val += 0.02 * (dcorner_old - dcorner_new)  # prefer closer to corner

        if best is None:
            best, best_val = (dx, dy), val
        else:
            if pursuer:
                if val > best_val:
                    best, best_val = (dx, dy), val
            else:
                if val > best_val:
                    best, best_val = (dx, dy), val

    if best is not None:
        return [int(best[0]), int(best[1])]

    # Fallback: allow staying put if blocked by obstacle handling above
    return [0, 0]