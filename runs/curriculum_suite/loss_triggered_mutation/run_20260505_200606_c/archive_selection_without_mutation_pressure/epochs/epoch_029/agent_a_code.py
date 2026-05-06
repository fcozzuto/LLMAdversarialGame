def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = [0, 0]
    best_val = -10**18
    # Aim to take resources where we can beat the opponent earliest; if multiple, prefer those likely to be contested.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        val = 0
        # Avoid getting too close to opponent (prevents swapping into their safe line).
        d_opp = man(nx, ny, ox, oy)
        val -= 0.08 * d_opp

        # Compute contest advantage across resources.
        for rx, ry in resources:
            opp_d = man(ox, oy, rx, ry)
            our_d = man(nx, ny, rx, ry)

            # Earlier arrival matters most; also reward being on the same row to mirror common safe sweeps.
            time_gain = opp_d - our_d  # positive if we are closer
            row_gap = abs(ny - ry)
            row_bonus = 0
            if row_gap == 0:
                row_bonus = 2.4
            elif row_gap == 1:
                row_bonus = 1.4
            elif row_gap == 2:
                row_bonus = 0.6

            # If opponent is very close to a resource, heavily punish letting them keep the lead.
            pressure = 0
            if opp_d <= 2:
                pressure = 2.6
            elif opp_d <= 4:
                pressure = 1.2

            # Small preference to move toward generally good areas (closer resources).
            closeness = -0.06 * our_d

            val += time_gain * 2.0 + row_bonus + pressure * (1 if time_gain > 0 else -0.6) + closeness

        # Mild tie-break: keep moving generally toward upper-right unless it harms contest.
        val += 0.01 * (nx - sx) + 0.005 * (ny - sy)

        if val > best_val:
            best_val = val
            best = [dx, dy]

    return [best[0], best[1]]