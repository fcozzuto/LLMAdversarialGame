def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    target_scores = []
    if resources:
        for rx, ry in resources:
            d_self = cheb(sx, sy, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Prefer resources we can reach sooner; tie-break by farther from opponent (safer to "own")
            target_scores.append((d_opp - d_self, -d_opp, rx, ry))
        target_scores.sort(reverse=True)
        best_resource = (target_scores[0][2], target_scores[0][3])
    else:
        best_resource = None

    def resource_occupied(nx, ny):
        for rx, ry in resources:
            if rx == nx and ry == ny:
                return True
        return False

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if best_resource is None:
            # Spiral toward the corner opposite to opponent, staying away from obstacles only via ok()
            tx = 7 if ox < 4 else 0
            ty = 7 if oy < 4 else 0
            score = cheb(nx, ny, tx, ty) * -1
        else:
            rx, ry = best_resource
            # Main: decrease distance to chosen resource
            d_self_next = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            # Interference: if we get closer than opponent, big bonus
            score = (d_opp - d_self_next) * 100 - d_self_next

            # If stepping onto any resource, strong bonus
            if resource_occupied(nx, ny):
                score += 10000

            # If opponent is also near this resource, prefer moves that increase their distance
            d_opp_next_est = cheb(nx, ny, ox, oy)  # proxy: stay away to reduce their ability to collide
            score += d_opp_next_est * 0.5

        # Deterministic tie-break: prefer lexicographically smaller delta after score
        candidates.append((score, dx, dy))

    candidates.sort(reverse=True)
    return [int(candidates[0][1]), int(candidates[0][2])] if candidates else [0, 0]