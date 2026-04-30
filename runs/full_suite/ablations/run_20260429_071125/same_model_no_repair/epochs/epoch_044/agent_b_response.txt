def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_t = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        us = cheb(sx, sy, rx, ry)
        op = cheb(ox, oy, rx, ry)
        # Prefer resources we can potentially secure (us <= op), then maximize lead (op-us).
        key = (0 if us <= op else 1, -(op - us), us, rx * 8 + ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_mv_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        usn = cheb(nx, ny, tx, ty)
        # Also discourage moving to positions that make the opponent much closer.
        opn = cheb(ox, oy, tx, ty)
        key = (usn, 0 if usn <= opn else 1, usn - opn, (nx, ny)[0] * 8 + (nx, ny)[1])
        if best_mv_key is None or key < best_mv_key:
            best_mv_key = key
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]