def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_step():
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            if resources:
                # Prefer cells that make us reach a resource first; break ties toward closeness.
                s = None
                for r in resources:
                    if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                        continue
                    rx, ry = r[0], r[1]
                    myd = cheb(nx, ny, rx, ry)
                    oppd = cheb(ox, oy, rx, ry)
                    # Negative means "good" (we are likely ahead); weight opp distance to contest.
                    val = (myd - 0.85 * oppd, myd)
                    if s is None or val < s:
                        s = val
                # If no valid resources, fallback
                if s is None:
                    val = (1e18, 1e18)
                else:
                    val = s
                # Also incorporate immediate separation to reduce opponent interference.
                sep = cheb(nx, ny, ox, oy)
                candidate = (val[0], val[1], -sep, dx, dy, nx, ny)
            else:
                sep = cheb(nx, ny, ox, oy)
                candidate = (-sep, 0, 0, dx, dy, nx, ny)
            if best is None or candidate < best:
                best = candidate
        if best is None:
            return [0, 0]
        return [best[3], best[4]]

    return best_step()