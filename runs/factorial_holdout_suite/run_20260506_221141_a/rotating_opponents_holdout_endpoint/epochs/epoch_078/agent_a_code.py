def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_val = None

    res_set = set(resources)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # If we can collect now, prioritize deterministically.
        if (nx, ny) in res_set:
            val = -10**6
        else:
            val = 10**9
            # Race to resources: minimize (my_dist - opp_dist); tie-break by my_dist and by x,y.
            for rx, ry in resources:
                md = cheb(nx, ny, rx, ry)
                od = cheb(ox, oy, rx, ry)
                race = md - od
                cand = (race * 1000) + md  # opp-advantage dominates
                if cand < val:
                    val = cand
                elif cand == val:
                    if (rx, ry) < (resources[0][0], resources[0][1]):
                        pass

            # Slight preference for moving toward board center to avoid dead-ends.
            cx, cy = 3.5, 3.5
            dcur = abs(nx - cx) + abs(ny - cy)
            val += int(dcur * 2)

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)
        elif val == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]