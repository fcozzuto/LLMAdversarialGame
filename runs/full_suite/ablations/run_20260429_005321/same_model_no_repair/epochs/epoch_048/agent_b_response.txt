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

    def best_target():
        best = resources[0]
        bestv = -10**18
        for rx, ry in resources:
            sd = king_dist(sx, sy, rx, ry)
            od = king_dist(ox, oy, rx, ry)
            v = (od - sd) * 60 - sd
            if v > bestv:
                bestv = v
                best = (rx, ry)
        return best

    tx, ty = best_target()
    opp_target = None
    best_opp_adv = -10**18
    for rx, ry in resources:
        sd = king_dist(ox, oy, rx, ry)
        od = king_dist(sx, sy, rx, ry)
        v = (od - sd) * 50 - sd
        if v > best_opp_adv:
            best_opp_adv = v
            opp_target = (rx, ry)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue

        sd_new = king_dist(nx, ny, tx, ty)
        sd_now = king_dist(sx, sy, tx, ty)
        od_new = king_dist(nx, ny, ox, oy)
        opp_sd = king_dist(ox, oy, tx, ty)

        # Primary: win race to chosen target
        score = (opp_sd - sd_new) * 80 - sd_new

        # Secondary: progress toward our target
        score += (sd_now - sd_new) * 12

        # Blocking/interference: if opponent is closer to their best resource, reduce their reach
        if opp_target is not None:
            ptx, pty = opp_target
            opp_res_dist_now = king_dist(ox, oy, ptx, pty)
            opp_res_dist_new = king_dist(ox, oy, ptx, pty)
            # If we move closer to the opponent's best resource, discourage them from claiming it
            our_dist_oppres_now = king_dist(sx, sy, ptx, pty)
            our_dist_oppres_new = king_dist(nx, ny, ptx, pty)
            score += (our_dist_oppres_now - our_dist_oppres_new) * 10

        # Avoid moving adjacent to opponent if we can't gain immediately
        if od_new <= 1 and sd_new >= sd_now:
            score -= 25

        # Small preference for staying nearer the center of remaining resources
        score -= min(king_dist(nx, ny, rx, ry) for rx, ry in resources) * 0.8

        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]