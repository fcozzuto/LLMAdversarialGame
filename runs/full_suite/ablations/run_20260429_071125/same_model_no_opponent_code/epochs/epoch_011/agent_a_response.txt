def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(p) for p in observation.get("resources", [])]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(nx, ny): return 0 <= nx < w and 0 <= ny < h
    def safe(nx, ny): return inb(nx, ny) and (nx, ny) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy
    def obst_adj(nx, ny):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0: continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in obstacles:
                    c += 1
        return c

    # Choose a resource target by race advantage: (opponent_dist - self_dist) descending
    target = None
    best_adv = -10**9
    best_d = 10**9
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        if adv > best_adv or (adv == best_adv and sd < best_d):
            best_adv, best_d, target = adv, sd, (rx, ry)

    if target is None:
        # No visible resources; drift away from opponent toward safer area
        best = (0, 0, -10**9)
        for dx, dy in deltas:
            nx, ny = x + dx, y + dy
            if not safe(nx, ny): continue
            d_op = cheb(nx, ny, ox, oy)
            val = d_op - 0.6 * obst_adj(nx, ny)
            if val > best[2]: best = (dx, dy, val)
        return [best[0], best[1]]

    tx, ty = target
    cur_d = cheb(x, y, tx, ty)

    best_dx, best_dy, best_val = 0, 0, -10**9
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if not safe(nx, ny): continue
        nd = cheb(nx, ny, tx, ty)
        # Prefer reducing distance; if equal, prefer improving race vs opponent.
        my_adv = cheb(ox, oy, tx, ty) - nd
        opp_close = cheb(nx, ny, ox, oy)
        val = (10 if nd < cur_d else 0) + (nd == cur_d) * 2 + my_adv - 0.35 * obst_adj(nx, ny) + 0.08 * opp_close
        if val > best_val or (val == best_val and (nd < cheb(x, y, tx, ty))):
            best_dx, best_dy, best_val = dx, dy, val

    return [int(best_dx), int(best_dy)]