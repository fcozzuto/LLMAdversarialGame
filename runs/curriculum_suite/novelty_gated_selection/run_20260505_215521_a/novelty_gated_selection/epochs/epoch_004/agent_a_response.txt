def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick target that we are relatively closer to (favor stealing). If none, head to opponent.
    if resources:
        best = None
        best_val = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            tx, ty = r[0], r[1]
            sd = man(sx, sy, tx, ty)
            od = man(ox, oy, tx, ty)
            val = sd - od
            if best_val is None or val < best_val or (val == best_val and (sd < best_val_sd or (sd == best_val_sd and (tx, ty) < best))):
                best_val = val
                best_val_sd = sd
                best = (tx, ty)
        tx, ty = best
    else:
        tx, ty = ox, oy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # If opponent is closer to our chosen target, slightly bias toward moves that also reduce opponent distance.
    opp_bias = 1 if resources else 0

    best_move = (0, 0)
    best_tuple = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d_self = man(nx, ny, tx, ty)
        d_opp = man(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: if chasing resources, avoid letting opponent get too good.
        # Extra: prefer staying in place if all else ties to be robust.
        if resources:
            d_oppt = man(ox, oy, tx, ty)
            score = (d_self, d_oppt - d_self, (nx, ny) != (sx, sy), d_opp)
        else:
            score = (d_self, (nx, ny) != (sx, sy), d_opp)
        if best_tuple is None or score < best_tuple:
            best_tuple = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]