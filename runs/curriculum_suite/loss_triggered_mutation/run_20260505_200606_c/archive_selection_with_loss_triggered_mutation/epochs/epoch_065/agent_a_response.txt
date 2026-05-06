def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Pick a target resource where we have advantage vs opponent (opp farther).
    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            d_self = man(sx, sy, rx, ry)
            d_opp = man(ox, oy, rx, ry)
            # advantage: smaller (self - opp) is better; also prefer closer for both.
            key = (d_self - d_opp, d_self, -d_opp, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        # If no resources, retreat to a corner-aligned safe move that also distances opponent.
        tx, ty = 0 if ox > sx else w - 1, 0 if oy > sy else h - 1

    # If opponent is significantly closer to the chosen target, switch to next best resource.
    if resources:
        d_self = man(sx, sy, tx, ty)
        d_opp = man(ox, oy, tx, ty)
        if d_opp + 1 < d_self:
            best_res = None
            best_key = None
            for rx, ry in resources:
                d1 = man(sx, sy, rx, ry)
                d2 = man(ox, oy, rx, ry)
                key = (d1 - d2, d1, -d2, rx, ry)
                # require some advantage or at least not terrible
                if d2 + 1 < d1 or (d1 <= d2):
                    if best_key is None or key < best_key:
                        best_key = key
                        best_res = (rx, ry)
            if best_res is not None:
                tx, ty = best_res

    cur_self_to_opp = man(sx, sy, ox, oy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dres = man(nx, ny, tx, ty)
        dopp = man(nx, ny, ox, oy)
        # Score: prioritize making ourselves closer to target while pushing opponent farther.
        # Also keep some distance from opponent to avoid being contested at turn end.
        score = (dres, -dopp, abs(nx - tx) + abs(ny - ty) + (0 if dx == 0 or dy == 0 else 0.1))
        # Add penalty if we move closer to opponent too much.
        if dopp < cur_self_to_opp - 1:
            score = (score[0] + 2, score[1], score[2])

        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]