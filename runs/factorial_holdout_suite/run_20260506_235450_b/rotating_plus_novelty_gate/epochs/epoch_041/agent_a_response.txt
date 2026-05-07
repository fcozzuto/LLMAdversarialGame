def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = (0, 0)
    best_val = -10**18
    # Deterministic tie-break: first in moves list wins if equal.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            continue

        immediate = 0
        if any(nx == rx and ny == ry for rx, ry in resources):
            immediate = 100000

        val = immediate
        # Race/contest logic: prefer resources we can reach strictly earlier.
        for rx, ry in resources:
            d_us = cheb(nx, ny, rx, ry)
            d_op = cheb(ox, oy, rx, ry)
            if d_us == 0:
                continue
            if d_us < d_op:
                val += (d_op - d_us) * 50
                # small bias toward closer winning routes
                val += max(0, 8 - d_us) * 2
            else:
                # penalize committing to resources opponent can take first
                val -= d_us * 1

        # Interceptor-ish bias: if we can't win many, reduce opponent access by moving closer to where they currently are.
        val -= cheb(nx, ny, ox, oy) * 0.5

        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]