def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw = observation.get("grid_width", 8)
    gh = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    if not resources:
        return [0, 0]

    obs = set((x, y) for x, y in obstacles)

    def inb(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def king_dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    # Pick a target that we are closest-to relative to the opponent.
    # If all are bad, still pick least-worst.
    def target_score_at(posx, posy, rx, ry):
        sd = king_dist(posx, posy, rx, ry)
        od = king_dist(ox, oy, rx, ry)
        return (od - sd) * 100 - sd

    best_t = resources[0]
    best_ts = -10**18
    for rx, ry in resources:
        ts = target_score_at(sx, sy, rx, ry)
        if ts > best_ts:
            best_ts = ts
            best_t = (rx, ry)
    tx, ty = best_t

    # Evaluate each move by (1) our advantage to best resource, (2) distance to chosen target,
    # (3) avoid moves that improve opponent's advantage too much on any resource.
    best_move = (0, 0)
    best_move_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            nx, ny = sx, sy

        # Our best advantage after this move
        top_adv = -10**18
        top_res = None
        top2 = []
        for rx, ry in resources:
            sd = king_dist(nx, ny, rx, ry)
            od = king_dist(ox, oy, rx, ry)
            adv = od - sd
            if adv > top_adv:
                top_adv = adv
                top_res = (rx, ry)
            # keep a small list for opponent-adv penalty
            # opponent-adv means "opponent is closer than us" after our move (i.e., sd > od)
            opp_adv = sd - od
            top2.append(opp_adv)
        top2.sort(reverse=True)
        opp_pen = (top2[0] if top2 else 0) * 1.5 + (top2[1] if len(top2) > 1 else 0) * 0.5

        # distance shaping towards current target
        sd_t = king_dist(nx, ny, tx, ty)
        # Small preference for staying closer to target even if another resource is locally better
        move_score = top_adv * 100 - sd_t - opp_pen

        if move_score > best_move_score:
            best_move_score = move_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]