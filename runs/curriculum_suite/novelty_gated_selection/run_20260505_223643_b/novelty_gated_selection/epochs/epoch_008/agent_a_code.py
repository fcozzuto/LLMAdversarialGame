def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    opp_dists = []
    for rx, ry in resources:
        opp_dists.append((cheb(ox, oy, rx, ry), rx, ry))
    opp_dists.sort(key=lambda t: t[0])
    top_opp = opp_dists[:4]  # most contested targets

    best_val = -10**18
    best_move = (0, 0)

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h or (nx, ny) in obstacles:
            continue

        # Primary objective: maximize being closer than the opponent on contested targets.
        val = 0.0
        # Secondary objective: if we can't win contested targets, switch to a resource with high "swing".
        for do, rx, ry in top_opp:
            ds = cheb(nx, ny, rx, ry)
            adv = do - ds  # positive => we are closer than opponent (at/near acquisition)
            val += 120.0 * adv - 4.0 * ds

        # Tertiary objective: pursue best remaining resource for us while avoiding giving the opponent a big lead.
        best_ds = 10**9
        worst_adv = 10**9
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            if ds < best_ds:
                best_ds = ds
            do = cheb(ox, oy, rx, ry)
            adv = do - ds
            if adv < worst_adv:
                worst_adv = adv  # most negative advantage indicates letting them dominate

        # Encourage moving toward a reasonable target unless it hands the opponent a decisive advantage.
        val += 2.0 * (10 - best_ds)
        val -= 30.0 * (0 - worst_adv) if worst_adv < 0 else 0.0

        # Small directional bias to break ties consistently (toward increasing x then y).
        val += 0.001 * (nx - sx) + 0.0001 * (ny - sy)

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]