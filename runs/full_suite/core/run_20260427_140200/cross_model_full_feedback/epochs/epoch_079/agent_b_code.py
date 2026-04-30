def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    mx, my = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Simple deterministic policy:
    # 1) If there is a resource, move toward the closest one not blocked.
    # 2) If no resource, move toward the center to minimize risk and approach midpoints.
    best_dx = 0
    best_dy = 0

    if resources:
        best_r = None
        best_score = 10**9
        for rx, ry in resources:
            dme = cheb((mx, my), (rx, ry))
            dop = cheb((ox, oy), (rx, ry))
            # Prefer resources closer to me and farther from opponent to reduce contest
            score = dme - dop
            if score < best_score:
                best_score = score
                best_r = (rx, ry)
        if best_r is not None:
            tx, ty = best_r
            dx = 0 if tx == mx else (1 if tx > mx else -1)
            dy = 0 if ty == my else (1 if ty > my else -1)
            if legal(mx + dx, my + dy):
                best_dx, best_dy = dx, dy
            else:
                # if blocked, try to step along row/col separately to same target
                if legal(mx + dx, my):
                    best_dx, best_dy = dx, 0
                elif legal(mx, my + dy):
                    best_dx, best_dy = 0, dy
                else:
                    best_dx, best_dy = 0, 0
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if cx == mx else (1 if cx > mx else -1)
        dy = 0 if cy == my else (1 if cy > my else -1)
        if legal(mx + dx, my + dy):
            best_dx, best_dy = dx, dy
        else:
            if legal(mx + dx, my):
                best_dx, best_dy = dx, 0
            elif legal(mx, my + dy):
                best_dx, best_dy = 0, dy
            else:
                best_dx, best_dy = 0, 0

    # Fallback deterministic guard
    if best_dx not in (-1, 0, 1) or best_dy not in (-1, 0, 1):
        best_dx, best_dy = 0, 0
    return [best_dx, best_dy]