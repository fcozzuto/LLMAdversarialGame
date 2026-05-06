def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    my_pos = (sx, sy)
    opp_pos = (ox, oy)

    # Pick the resource where we are relatively closer than the opponent; otherwise fall back to our closest.
    best_r = None
    best_val = None
    best_close = None
    best_close_d = None
    for r in resources:
        d_my = dist2(my_pos, r)
        d_opp = dist2(opp_pos, r)
        v = (d_opp - d_my) - 0.001 * d_my
        if best_val is None or v > best_val:
            best_val = v
            best_r = r
        if best_close_d is None or d_my < best_close_d:
            best_close_d = d_my
            best_close = r

    target = best_r if best_val is not None and best_val >= 0 else best_close

    # If target is somehow invalid (shouldn't happen), stay.
    if target is None:
        return [0, 0]

    tx, ty = target
    curr_d = dist2(my_pos, target)

    # Move deterministically: choose valid step that most reduces distance to target; tie-break by maximizing opponent-distance.
    best_step = (0, 0)
    best_step_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_to_target = dist2((nx, ny), target)
        d_opp_next = dist2((ox, oy), target)
        step_val = (curr_d - d_to_target) * 1000 + (d_opp_next - d_to_target)
        if best_step_val is None or step_val > best_step_val or (step_val == best_step_val and (dx, dy) < best_step):
            best_step_val = step_val
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]