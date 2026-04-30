def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick best target by advantage and proximity.
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = dist(sx, sy, rx, ry)
        od = dist(ox, oy, rx, ry)
        adv = od - sd
        key = (adv, -sd, rx, ry)  # maximize adv, then prefer closer
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)
    tx, ty = best_t

    # If opponent is closer to some resource, bias towards that "contested" resource.
    contested_t = None
    contested_adv = None
    for rx, ry in resources:
        od = dist(ox, oy, rx, ry)
        sd = dist(sx, sy, rx, ry)
        diff = od - sd
        # opponent imminent: very small od
        key = (od, -diff, rx, ry)
        if contested_t is None or key < (contested_adv[0], contested_adv[1], contested_adv[2], contested_adv[3]) if False else False:
            pass
    # Simple deterministic contested selection:
    for rx, ry in resources:
        od = dist(ox, oy, rx, ry)
        sd = dist(sx, sy, rx, ry)
        if od <= sd and (contested_t is None or od < dist(ox, oy, contested_t[0], contested_t[1]) or
                         (od == dist(ox, oy, contested_t[0], contested_t[1]) and (sd - od) > (dist(sx, sy, contested_t[0], contested_t[1]), dist(ox, oy, contested_t[0], contested_t[1]))[0])):
            contested_t = (rx, ry)
    if contested_t is not None:
        cx, cy = contested_t
        # Use contested target only if it improves our advantage over the chosen target.
        if dist(sx, sy, cx, cy) - dist(ox, oy, cx, cy) < dist(sx, sy, tx, ty) - dist(ox, oy, tx, ty):
            tx, ty = cx, cy

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = None

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Primary: approach target faster than opponent.
        nds = dist(nx, ny, tx, ty)
        ndo = dist(ox, oy, tx, ty)
        my_adv = ndo - nds

        # Secondary: avoid enabling opponent capture of some nearby resource.
        opp_gain = 0
        for rx, ry in resources:
            dcr = dist(nx, ny, rx, ry) - dist(ox, oy, rx, ry)
            # If we move such that opponent becomes relatively closer, penalize.
            opp_gain += max(0, -dcr)

        # Tertiary: discourage moving into/near obstacle-adjacent traps (simple count).
        adj_obs = 0
        for ddx, ddy in candidates:
            tx2, ty2 = nx + ddx, ny + ddy
            if 0 <= tx2 < w and 0 <= ty2 < h and (tx2, ty2) in obstacles:
                adj_obs += 1

        # Safety: prefer being at least as far from opponent as target distance improves.
        d_opp = dist(nx, ny, ox, oy)

        val = (my_adv, -nds, d_opp, -opp_gain, -adj_obs, nx, ny)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]