def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    resources = [tuple(r) for r in observation.get("resources", [])]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cur_opp_d = cheb(sx, sy, ox, oy)

    def best_contest_for_move(nx, ny):
        if not resources:
            return (0, 0, 0)  # gain, selfd, oppd
        best_gain = -10**9
        best_selfd = 10**9
        best_oppd = 10**9
        for rx, ry in resources:
            selfd = cheb(nx, ny, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            gain = oppd - selfd
            if gain > best_gain or (gain == best_gain and selfd < best_selfd) or (gain == best_gain and selfd == best_selfd and oppd < best_oppd):
                best_gain, best_selfd, best_oppd = gain, selfd, oppd
        return best_gain, best_selfd, best_oppd

    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        gain, selfd, oppd = best_contest_for_move(nx, ny)
        next_opp_d = cheb(nx, ny, ox, oy)
        score = 0
        score += 80 * gain
        score += 8 * (cur_opp_d - next_opp_d)
        if resources:
            score += 2 * (oppd - selfd)  # tighter contest preference
            score -= selfd  # still try to reach something
        else:
            score += 2 * (cur_opp_d - next_opp_d)

        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]