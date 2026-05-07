def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    gw = int(observation.get("grid_width", 8) or 8)
    gh = int(observation.get("grid_height", 8) or 8)
    def inb(x, y): return 0 <= x < gw and 0 <= y < gh

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inb(px, py):
                obstacles.add((px, py))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inb(rx, ry) and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb_dist(x1, y1, x2, y2):
        dx = abs(x1 - x2); dy = abs(y1 - y2)
        return dx if dx > dy else dy

    moves = [(0, 0),(1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)]
    best_move = (0, 0)
    best_val = -10**9

    center = (gw // 2, gh // 2)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        if resources:
            val = -cheb_dist(nx, ny, center[0], center[1]) * 0.01
            for rx, ry in resources:
                myd = cheb_dist(nx, ny, rx, ry)
                opd = cheb_dist(ox, oy, rx, ry)
                # Favor resources we can secure earlier
                lead = opd - myd
                # Extra contest pressure if resource lies on the opponent's "sweep-ish" axes
                axis_contest = (rx == ox) + (ry == oy)
                near_me = cheb_dist(nx, ny, rx, ry)
                val += (lead * 3.0) - (near_me * 1.0) + axis_contest * 0.8
            # Small bias for progressing rather than dithering
            val += (cheb_dist(nx, ny, center[0], center[1]) < cheb_dist(sx, sy, center[0], center[1])) * 0.05
        else:
            val = -cheb_dist(nx, ny, center[0], center[1])

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]