def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    # Pick an immediate "best" resource to aim for based on relative reach.
    best_target = None
    best_gain = -10**9
    for rx, ry in resources:
        our = md(sx, sy, rx, ry)
        opp = md(ox, oy, rx, ry)
        # gain >0 means we are closer (or opp is farther).
        gain = opp - our
        # tie-break: prefer closer overall to reduce risk of stagnation.
        if gain > best_gain or (gain == best_gain and our < md(sx, sy, best_target[0], best_target[1]) if best_target else True):
            best_gain = gain
            best_target = (rx, ry)
    tx, ty = best_target

    # If opponent is already much closer to all resources, switch to denial:
    # choose move that maximizes the opponent's nearest resource distance after our move.
    # Otherwise, move toward our chosen target while keeping opponent's reach in check.
    any_opp_close = False
    for rx, ry in resources:
        if md(ox, oy, rx, ry) + 1 < md(sx, sy, rx, ry):
            any_opp_close = True
            break

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        if any_opp_close:
            # denial: maximize opponent's best achievable distance to any resource after we move
            # (our action may affect only indirectly; still prefer spacing that blocks sweeping).
            opp_best = 10**9
            for rx, ry in resources:
                # if opponent could go straight toward a resource, distance is what matters
                d = md(ox, oy, rx, ry)
                if d < opp_best:
                    opp_best = d
            # encourage positions that are farther from opponent, to disrupt sweep patterns
            val = opp_best + 0.3 * md(nx, ny, ox, oy)
        else:
            # pursuit + relative threat reduction
            our_d = md(nx, ny, tx, ty)
            opp_d_to_same = md(ox, oy, tx, ty)
            # encourage getting closer, but if opponent is also close, prioritize moves that worsen their odds.
            val = -our_d + 0.55 * (opp_d_to_same - md(nx, ny, tx, ty))
            # small secondary: avoid moving adjacent to obstacles edge cases by preferring higher local resource density
            # (deterministic, limited computation)
            local = 0
            for rx, ry in resources:
                if md(nx, ny, rx, ry) <= 2:
                    local += 1
            val += 0.05 * local

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move