def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y): 
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target(tposx, tposy, oex, oey):
        if not resources: 
            return None
        best = None
        best_key = None
        for cx, cy in resources:
            sd = cheb(tposx, tposy, cx, cy)
            od = cheb(oex, oey, cx, cy)
            key = (od - sd, -sd, -cx, -cy)
            if best_key is None or key > best_key:
                best_key = key
                best = (cx, cy)
        return best

    def step_toward(tx, ty, px, py):
        # greedy one-step toward target using cheb distance
        best = (px, py)
        bestd = cheb(px, py, tx, ty)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = px + dx, py + dy
                if not inb(nx, ny) or (nx, ny) in obs:
                    continue
                d = cheb(nx, ny, tx, ty)
                if d < bestd or (d == bestd and (nx, ny) < best):
                    bestd = d
                    best = (nx, ny)
        return best

    target = best_target(sx, sy, ox, oy)
    if target is None:
        return [0, 0]
    tx, ty = target

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            our_d = cheb(nx, ny, tx, ty)
            oppnx, oppny = step_toward(tx, ty, ox, oy)
            opp_d = cheb(oppnx, oppny, tx, ty)

            # Also slight incentive to move onto resources if possible
            on_resource = 0
            for rx, ry in resources:
                if rx == nx and ry == ny:
                    on_resource = 1
                    break

            # Bonus for increasing distance between us and opponent while pursuing
            dist_away = cheb(nx, ny, oppnx, oppny)

            # Primary: make us closer than opponent; Secondary: minimize our distance; Tertiary: deterministic
            key = (-(our_d - opp_d) + 3 * on_resource, -(-dist_away), -our_d, -dx, -dy, nx, ny)
            candidates.append((key, dx, dy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True, key=lambda x: x[0])
    return [int(candidates[0][1]), int(candidates[0][2])]