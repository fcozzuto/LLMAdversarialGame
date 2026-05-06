def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    obs = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    # No resources: keep maneuvering away from opponent while trending to center
    if not resources:
        bestm = (0, 0)
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not inb(nx, ny):
                continue
            d_opp = cheb(nx, ny, ox, oy)
            v = d_opp * 1000 - (abs(nx - cx) + abs(ny - cy)) * 2
            if v > bestv:
                bestv = v
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not inb(nx, ny):
            continue

        center_bias = -(abs(nx - cx) + abs(ny - cy)) * 0.1
        move_v = center_bias

        # Evaluate best outcome over all visible resources: either steal advantage or deny by closing gap.
        for rx, ry in resources:
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)

            # stealing: prefer resources where opponent isn't closer
            if self_d <= opp_d:
                steal = (opp_d - self_d) * 120 - self_d * 3
                # small preference for more "reachable" targets (tie-breaking)
                steal -= abs((nx + nx + 0) - (rx + rx)) * 0.0
                if steal > move_v:
                    move_v = steal
            else:
                # denial: reduce opponent's lead by moving into contested zone
                denial = (self_d - opp_d) * -60 + (opp_d - self_d) * 10
                # denial should still be meaningful; discourage far-from-resource moves
                denial -= self_d * 2
                if denial > move_v:
                    move_v = denial

        # Additional safety: avoid walking into tight symmetric traps
        d_opp_now = cheb(nx, ny, ox, oy)
        if d_opp_now <= 1:
            move_v -= 20

        if move_v > bestv:
            bestv = move_v
            bestm = (dx, dy)

    return [bestm[0], bestm[1]]