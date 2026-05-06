def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    # Choose a target resource: the one we're closest to that the opponent is not dramatically closer to.
    best_res = None
    best_res_score = -10**18
    for rx, ry in resources:
        our = man(sx, sy, rx, ry)
        opp = man(ox, oy, rx, ry)
        # Favor resources where we are competitive, but still allow captures that reduce opponent lead.
        score = (opp - our) * 3 - our
        if score > best_res_score:
            best_res_score = score
            best_res = (rx, ry)
    tr, ty = best_res

    # Also define an "intercept" target: a point near the opponent heading, approximated by best resource for opponent.
    opp_res = None
    opp_best = 10**18
    for rx, ry in resources:
        d = man(ox, oy, rx, ry)
        if d < opp_best:
            opp_best = d
            opp_res = (rx, ry)
    irx, iry = opp_res

    # If opponent is very close to a resource, prioritize moving to reduce their advantage.
    opp_pressure = 1 if man(ox, oy, irx, iry) <= 2 else 0

    # Evaluate moves: maximize (opponent advantage we deny) + keep progress toward a good target.
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        # Direct competition over target resource
        our_d = man(nx, ny, tr, ty)
        opp_d = man(ox, oy, tr, ty)
        deny = opp_d - our_d  # bigger means we are closer

        # If pressured, also reduce opponent's closeness to their nearest resource
        if opp_pressure:
            our2 = man(nx, ny, irx, iry)
            opp2 = man(ox, oy, irx, iry)
            deny2 = opp2 - our2
        else:
            deny2 = 0

        # Small tie-break: align y with target row, and avoid drifting away from board center-ish
        row_align = -abs(ny - ty)
        center_bias = -(abs(nx - (w - 1) / 2.0) + abs(ny - (h - 1) / 2.0)) * 0.01

        val = deny * 10 + deny2 * 6 + our_d * (-0.6) + row_align * 2 + center_bias

        # Nudge away from getting stuck behind obstacles: prefer steps that change both coords toward target when possible
        if dx != 0 and dy != 0:
            toward = (1 if tr > nx else (-1 if tr < nx else 0)) * dx + (1 if ty > ny else (-1 if ty < ny else 0)) * dy
            val += toward * 0.2

        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]