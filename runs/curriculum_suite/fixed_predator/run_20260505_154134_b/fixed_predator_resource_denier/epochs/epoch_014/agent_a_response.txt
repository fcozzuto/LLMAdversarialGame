def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', []) or []
    obst_list = observation.get('obstacles', []) or []
    obstacles = set((p[0], p[1]) for p in obst_list)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    def manh(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx + dy

    # Choose target resource that maximizes a denial-aware value.
    best_t = None
    best_v = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        dself = cheb(sx, sy, rx, ry)
        dopp = cheb(ox, oy, rx, ry)
        # Bias: prefer resources closer to us; also prefer where opponent is farther.
        # Denial pressure increases as opponent gets closer.
        v = (dopp - dself, -dself, -manh(sx, sy, rx, ry), rx, ry)
        if best_v is None or v > best_v:
            best_v = v
            best_t = (rx, ry)

    # If no usable resources: directly deny by moving toward opponent.
    if best_t is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_t

    # Evaluate next-step moves with obstacle avoidance; pick best deterministic.
    def move_value(nx, ny):
        # primary: get closer to target resource
        ds = cheb(nx, ny, tx, ty)
        # secondary: increase distance from opponent to denial (or reduce if targeting denial)
        if best_t is None:
            # chasing opponent for denial
            dopp = cheb(nx, ny, ox, oy)
            score = (-dopp, ds)
        else:
            do = cheb(ox, oy, tx, ty)
            # how much we reduce opponent advantage by moving
            # (approx) compare our new distance vs current distance
            dself_now = cheb(sx, sy, tx, ty)
            score = (do - ds, -(ds), -(abs(nx - sx) + abs(ny - sy)))
        return score

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sc = move_value(nx, ny)
        # Deterministic tie-break: prefer lexicographically smaller dx,dy to keep stable.
        if best_score is None or sc > best_score or (sc == best_score and (dx, dy) < best_move):
            best_score = sc
            best_move = (dx, dy)

    # If all moves blocked (unlikely), stay.
    return [best_move[0], best_move[1]]