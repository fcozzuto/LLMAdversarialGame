def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def blocked(x, y):
        return (x, y) in obs or not (0 <= x < w and 0 <= y < h)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    candidates = []
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not (isinstance(rx, int) and isinstance(ry, int)):
            continue
        if blocked(rx, ry):
            continue
        du = cheb(sx, sy, rx, ry)
        dov = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach earlier; slight bias to shorter du.
        gain = (dov - du) * 100 - du
        candidates.append((gain, du, dov, rx, ry))
    if not candidates:
        return [0, 0]

    candidates.sort(reverse=True)
    best_gain, best_du, best_dov, tx, ty = candidates[0]

    # If we're not actually leading, switch to a resource that maximizes (our probability proxy):
    # use best of top few that gives largest positive differential, otherwise minimize our du.
    top = candidates[:5]
    lead = [c for c in top if c[2] - c[1] > 0]
    if lead:
        lead.sort(reverse=True)
        _, _, _, tx, ty = lead[0]
    else:
        top.sort(key=lambda c: (c[1], -c[0]))
        _, _, _, tx, ty = top[0]

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nu = cheb(nx, ny, tx, ty)
        nd = cheb(nx, ny, ox, oy)  # secondary: spread away from opponent if possible
        # Relative advantage after our move approximated by comparing distance to same target.
        # Opponent distance unchanged this turn; encourages our approach when contesting.
        rel = best_dov - nu
        # Also penalize moving away from target.
        dist_pen = nu
        score = rel * 50 + nd - dist_pen
        if best is None or score > best[0]:
            best = (score, dx, dy)
    if best is None:
        # fallback: try staying
        return [0, 0]
    return [best[1], best[2]]