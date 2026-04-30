def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                resources.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Mode: when opponent is near, prioritize stealing/blocking by targeting resources
    # that are relatively closer to us than to the opponent; otherwise go nearest.
    opp_close = md(sx, sy, ox, oy) <= 2

    best = None
    best_val = None
    for dx, dy, nx, ny in moves:
        if resources:
            if opp_close:
                # Score: maximize (opp_dist - self_dist) to the best resource for us,
                # also add a small preference for moving closer to that resource.
                best_gain = -10**9
                best_res_d = 10**9
                for rx, ry in resources:
                    d_me = md(nx, ny, rx, ry)
                    d_op = md(ox, oy, rx, ry)
                    gain = d_op - d_me
                    if gain > best_gain or (gain == best_gain and d_me < best_res_d):
                        best_gain = gain
                        best_res_d = d_me
                val = best_gain * 10 - best_res_d
                # Extra: if gain is poor, back off to increase distance from opponent.
                val -= md(nx, ny, ox, oy)
            else:
                # Normal: go to nearest resource; tie-break by also increasing distance from opponent.
                d_me = min(md(nx, ny, rx, ry) for rx, ry in resources)
                val = -d_me * 10 - md(nx, ny, ox, oy)
        else:
            # No resources visible: maximize distance from opponent (stay safe).
            val = md(nx, ny, ox, oy)

        if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best[0], best[1])):
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]