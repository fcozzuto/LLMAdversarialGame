def choose_move(observation):
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = p
            obstacles.add((x, y))
        except Exception:
            pass

    unclaimed = []
    for p in observation.get("unclaimed_cells", []) or []:
        try:
            x, y = p
            if (x, y) not in obstacles:
                unclaimed.append((x, y))
        except Exception:
            pass

    candidates = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if unclaimed:
        def best_cell():
            best = None
            best_d = 10**9
            for x, y in unclaimed:
                d = abs(x - sx) + abs(y - sy)
                if d < best_d or (d == best_d and (x, y) < best):
                    best_d = d
                    best = (x, y)
            return best
        tx, ty = best_cell()
    else:
        tx, ty = ox, oy

    best_move = None
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_to_target = abs(nx - tx) + abs(ny - ty)
        d_to_opp = abs(nx - ox) + abs(ny - oy)
        # Prefer minimizing distance to target; break ties by maximizing distance from opponent
        val = (-d_to_target) + (0.001 * d_to_opp)
        if val > best_val or (val == best_val and (nx, ny) < (sx + (best_move[0] if best_move else 0), sy + (best_move[1] if best_move else 0))):
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]