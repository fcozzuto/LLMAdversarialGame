def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    dirs = (-1, 0, 1)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def adj_obs(x, y):
        c = 0
        for dx in dirs:
            for dy in dirs:
                if dx == 0 and dy == 0: continue
                if (x + dx, y + dy) in obstacles: c += 1
        return c

    def best_target(px, py):
        if not resources:
            return (w // 2, h // 2)
        best = resources[0]; bestv = -10**18
        for (rx, ry) in resources:
            dme = cheb(px, py, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            v = (dop - dme) * 4.0 - dme * 1.0 - 0.7 * adj_obs(rx, ry)
            if dme < dop: v += 2.5
            # Keep away from opponent when resources are scarce
            v -= 0.08 * cheb(px, py, ox, oy)
            if v > bestv:
                bestv = v; best = (rx, ry)
        return best

    # Optional immediate interference: if opponent can take a resource next, move to contest that direction
    target = best_target(sx, sy)
    tx, ty = target

    # If opponent is closer to any resource right now, retarget to the one where we can at least reduce the lead
    if resources:
        best_lead = None
        for (rx, ry) in resources:
            dme = cheb(sx, sy, rx, ry)
            dop = cheb(ox, oy, rx, ry)
            if dme >= dop:  # opponent lead
                lead = dop - dme
                if best_lead is None or lead > best_lead[0]:
                    best_lead = (lead, rx, ry)
        if best_lead is not None:
            _, rx, ry = best_lead
            # If we are not able to beat it, switch to nearer among that and our prior target to keep options
            d_prior = cheb(sx, sy, tx, ty)
            d_new = cheb(sx, sy, rx, ry)
            if d_new <= d_prior + 1:
                tx, ty = rx, ry

    best_move = [0, 0]; best_score = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
                dx = 0; dy = 0
            nt = best_target(nx, ny)
            tx2, ty2 = nt
            dme2 = cheb(nx, ny, tx2, ty2)
            dop2 = cheb(ox, oy, tx2, ty2)
            score = (dop2 - dme2) * 4.0 - dme2 - 0.7 * adj_obs(tx2, ty2) - 0.08 * cheb(nx, ny, ox, oy)
            # Small preference: progress toward chosen tx,ty
            score += 0.15 * (cheb(nx, ny, tx, ty) * -1)
            if score > best_score:
                best_score = score
                best_move = [dx, dy]
    return [int(best_move[0]), int(best_move[1])]