def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        try:
            x, y = int(p[0]), int(p[1])
            obstacles.add((x, y))
        except Exception:
            pass

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, dict):
            pos = r.get("pos", None)
            if pos and len(pos) >= 2:
                x, y = pos[0], pos[1]
            else:
                x, y = r.get("x", None), r.get("y", None)
        else:
            x, y = (r[0], r[1]) if isinstance(r, (list, tuple)) and len(r) >= 2 else (None, None)
        if x is not None and y is not None:
            resources.append((int(x), int(y)))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not moves:
        return [0, 0]

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    my_corner = min(corners, key=lambda c: cheb(sx, sy, c[0], c[1]))
    opp_corner = min(corners, key=lambda c: cheb(ox, oy, c[0], c[1]))

    best_move = moves[0]
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy

        # Resource pressure: prefer moves that let us get closer than opponent.
        if resources:
            score = 0.0
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                oppd = cheb(ox, oy, rx, ry)
                # Big reward when we are relatively ahead.
                score += (oppd - myd) * 2.5
                # Small penalty to avoid very slow progress to any single resource.
                score -= myd * 0.25
                # Stronger bonus for capturing-proximity.
                if myd == 0:
                    score += 50.0
                elif myd == 1:
                    score += 8.0
            # Keep moving away from own corner only mildly; main drive is resources.
            score += -0.05 * cheb(nx, ny, my_corner[0], my_corner[1])
            # Slightly bias against letting opponent stay near their closest corner.
            score += 0.03 * cheb(nx, ny, opp_corner[0], opp_corner[1])
        else:
            # No resources visible: move to a corner that is closer to us than opponent.
            vmy = cheb(nx, ny, my_corner[0], my_corner[1])
            vop = cheb(nx, ny, opp_corner[0], opp_corner[1])
            score = (vop - vmy) * 2.0 - 0.02 * vmy

        if score > best_val:
            best_val = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]