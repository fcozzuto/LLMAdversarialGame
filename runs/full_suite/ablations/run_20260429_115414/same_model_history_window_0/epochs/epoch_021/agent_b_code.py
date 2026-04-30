def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))
    blocked = obstacles

    def dist(a, b, c, d):
        dx = a - c
        dy = b - d
        return abs(dx) + abs(dy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    # Candidate moves: dx,dy in {-1,0,1}
    best = [0, 0]
    best_score = -10**18

    # If resources exist, try to secure resources we are closer to than opponent,
    # otherwise move to reduce our distance to the best target.
    if resources:
        my_to = {}
        for rx, ry in resources:
            my_to[(rx, ry)] = dist(sx, sy, rx, ry)

        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in blocked:
                    continue
                # Avoid stepping into obvious trap near obstacle/opponent
                step_pen = 0
                # Small penalty if too close to opponent (encourage safer routes)
                step_pen += max(0, 3 - max(abs(nx - ox), abs(ny - oy))) * 2

                # Evaluate best resource for this step
                local_best = -10**18
                for rx, ry in resources:
                    myd = dist(nx, ny, rx, ry)
                    opd = dist(ox, oy, rx, ry)
                    # Lead bonus: strongly prefer resources where we are closer
                    score = (opd - myd) * 12 - myd
                    # If we land on a resource, huge
                    if nx == rx and ny == ry:
                        score += 10000
                    # Mild preference toward nearer resources to avoid wandering
                    local_best = max(local_best, score)

                total = local_best - step_pen
                if total > best_score:
                    best_score = total
                    best = [dx, dy]
    else:
        # No resources: move toward center while keeping distance from opponent
        cx, cy = w // 2, h // 2
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in blocked:
                    continue
                dcent = abs(nx - cx) + abs(ny - cy)
                dopp = abs(nx - ox) + abs(ny - oy)
                total = -dcent + min(10, dopp) * 0.8
                if total > best_score:
                    best_score = total
                    best = [dx, dy]

    return [int(best[0]), int(best[1])]